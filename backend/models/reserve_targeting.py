"""
Reserve targeting model for manganese exploration
Implements weighted geostatistical scoring index with fallback to ML if data is sufficient
"""

from sqlalchemy.orm import Session
from sqlalchemy import text, func
from database import SessionLocal
from models.schema import (
    Mine, Drillhole, AssayInterval, ReservePrediction, 
    PredictionExplanation, SourceTag
)
from datetime import datetime
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReserveTargetingModel:
    """
    Reserve targeting model with two approaches:
    1. Gradient-boosted classifier (if drillhole density is sufficient)
    2. Weighted geostatistical scoring index (fallback for sparse data)
    """
    
    # Minimum thresholds for supervised learning
    MIN_DRILLHOLES_PER_MINE = 20
    MIN_TOTAL_ASSAYS = 500
    
    # Scoring index weights (documented and transparent)
    SCORING_WEIGHTS = {
        'grade_idw': 0.35,           # Inverse-distance weighted grade
        'drillhole_proximity': 0.25, # Distance to nearest drillhole
        'ndvi_anomaly': 0.15,        # Vegetation anomaly
        'soil_moisture_anomaly': 0.15, # Soil moisture anomaly
        'lst_anomaly': 0.10,         # Land surface temperature anomaly
    }
    
    def __init__(self):
        self.db = SessionLocal()
        self.model_type = None  # Will be set after data density check
        self.ml_model = None
    
    def check_data_density(self) -> Dict:
        """
        Check if real drillhole density is sufficient for supervised learning
        
        Returns:
            Dict with density metrics and recommendation
        """
        try:
            # Get drillhole counts by mine
            drillhole_counts = self.db.query(
                Mine.id,
                Mine.name,
                func.count(Drillhole.id).label('drillhole_count')
            ).join(
                Drillhole, Mine.id == Drillhole.mine_id
            ).group_by(Mine.id, Mine.name).all()
            
            total_drillholes = sum(count for _, _, count in drillhole_counts)
            total_assays = self.db.query(AssayInterval).count()
            
            # Check density thresholds
            sufficient_density = (
                total_drillholes >= self.MIN_DRILLHOLES_PER_MINE and
                total_assays >= self.MIN_TOTAL_ASSAYS
            )
            
            density_info = {
                'total_drillholes': total_drillholes,
                'total_assays': total_assays,
                'min_drillholes_threshold': self.MIN_DRILLHOLES_PER_MINE,
                'min_assays_threshold': self.MIN_TOTAL_ASSAYS,
                'sufficient_for_ml': sufficient_density,
                'drillhole_by_mine': [
                    {'mine_id': mid, 'mine_name': name, 'count': count}
                    for mid, name, count in drillhole_counts
                ]
            }
            
            logger.info(f"Data density check: {density_info}")
            
            if sufficient_density:
                self.model_type = 'gradient_boosted_classifier'
                logger.info("Data density sufficient for gradient-boosted classifier")
            else:
                self.model_type = 'scoring_index'
                logger.info("Data density insufficient for ML, using scoring index approach")
            
            return density_info
            
        except Exception as e:
            logger.error(f"Error checking data density: {e}")
            self.model_type = 'scoring_index'  # Fallback to scoring index
            return {'sufficient_for_ml': False, 'error': str(e)}
    
    def train_ml_model(self):
        """
        Train gradient-boosted classifier for reserve targeting
        Only called if data density is sufficient
        """
        try:
            from xgboost import XGBClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import classification_report
            
            logger.info("Training gradient-boosted classifier...")
            
            # Prepare training data from assay intervals
            # Label: high-grade if Mn% > threshold (e.g., 25%)
            query = text("""
                SELECT 
                    ai.mn_percent,
                    ai.fe_percent,
                    ai.sio2_percent,
                    ai.al2o3_percent,
                    dh.total_depth_m,
                    CASE WHEN ai.mn_percent > 25 THEN 1 ELSE 0 END as high_grade
                FROM assay_intervals ai
                JOIN drillholes dh ON ai.drillhole_id = dh.id
                WHERE ai.mn_percent IS NOT NULL
            """)
            
            results = self.db.execute(query).fetchall()
            
            if len(results) < 100:
                logger.warning("Insufficient training samples, falling back to scoring index")
                self.model_type = 'scoring_index'
                return
            
            # Convert to DataFrame
            df = pd.DataFrame(results, columns=[
                'mn_percent', 'fe_percent', 'sio2_percent', 'al2o3_percent',
                'total_depth_m', 'high_grade'
            ])
            
            # Prepare features
            feature_cols = ['mn_percent', 'fe_percent', 'sio2_percent', 'al2o3_percent', 'total_depth_m']
            X = df[feature_cols].fillna(0)
            y = df['high_grade']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Train XGBoost classifier
            self.ml_model = XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                use_label_encoder=False,
                eval_metric='logloss'
            )
            
            self.ml_model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.ml_model.predict(X_test)
            report = classification_report(y_test, y_pred)
            logger.info(f"Model evaluation:\n{report}")
            
            logger.info("Gradient-boosted classifier trained successfully")
            
        except ImportError:
            logger.warning("XGBoost not available, falling back to scoring index")
            self.model_type = 'scoring_index'
        except Exception as e:
            logger.error(f"Error training ML model: {e}")
            self.model_type = 'scoring_index'
    
    def calculate_scoring_index(self, features: Dict) -> Tuple[float, str]:
        """
        Calculate weighted geostatistical scoring index
        
        Args:
            features: Dict with feature values
            
        Returns:
            Tuple of (likelihood_score_0_1, confidence_tier)
        """
        try:
            # Normalize features to 0-1 range
            normalized = self._normalize_features(features)
            
            # Calculate weighted sum
            score = 0.0
            for feature_name, weight in self.SCORING_WEIGHTS.items():
                feature_value = normalized.get(feature_name, 0.0)
                score += weight * feature_value
            
            # Clamp to 0-1
            score = max(0.0, min(1.0, score))
            
            # Determine confidence tier based on drillhole density
            drillhole_density = features.get('drillhole_density_500m', 0)
            if drillhole_density >= 5:
                confidence_tier = 'High'
            elif drillhole_density >= 2:
                confidence_tier = 'Medium'
            else:
                confidence_tier = 'Low'
            
            return score, confidence_tier
            
        except Exception as e:
            logger.error(f"Error calculating scoring index: {e}")
            return 0.5, 'Low'
    
    def _normalize_features(self, features: Dict) -> Dict:
        """Normalize features to 0-1 range"""
        normalized = {}
        
        # Grade: normalize to 0-1 (assume 0-50% range)
        grade = features.get('interpolated_grade_idw', 0)
        normalized['grade_idw'] = min(1.0, max(0.0, grade / 50.0))
        
        # Drillhole proximity: inverse distance (closer = higher)
        distance = features.get('distance_to_nearest_drillhole', 1000)
        normalized['drillhole_proximity'] = 1.0 / (1.0 + distance / 100.0)
        
        # Anomalies: assume -1 to 1 range, normalize to 0-1
        for anomaly in ['ndvi_anomaly', 'soil_moisture_anomaly', 'lst_anomaly']:
            value = features.get(anomaly, 0)
            normalized[anomaly] = (value + 1.0) / 2.0
            normalized[anomaly] = max(0.0, min(1.0, normalized[anomaly]))
        
        return normalized
    
    def generate_predictions(self, mine_id: Optional[int] = None):
        """
        Generate reserve predictions for cells
        
        Args:
            mine_id: Optional mine ID to filter (None = all mines)
        """
        try:
            logger.info(f"Generating reserve predictions (model_type: {self.model_type})...")
            
            # Check data density and set model type
            if self.model_type is None:
                self.check_data_density()
            
            # Train ML model if applicable
            if self.model_type == 'gradient_boosted_classifier' and self.ml_model is None:
                self.train_ml_model()
            
            # Get mines to process
            if mine_id:
                mines = [self.db.query(Mine).filter(Mine.id == mine_id).first()]
            else:
                mines = self.db.query(Mine).all()
            
            predictions_created = 0
            
            for mine in mines:
                if not mine:
                    continue
                
                # Get drillholes for this mine
                drillholes = self.db.query(Drillhole).filter(
                    Drillhole.mine_id == mine.id
                ).all()
                
                if not drillholes:
                    logger.warning(f"No drillholes for mine {mine.name}")
                    continue
                
                # Generate predictions for each drillhole location (as proxy for cells)
                for drillhole in drillholes:
                    if not drillhole.location:
                        continue
                    
                    # Calculate features (simplified - would use proper cell features)
                    features = self._get_cell_features(drillhole, mine.id)
                    
                    # Generate prediction
                    if self.model_type == 'gradient_boosted_classifier' and self.ml_model:
                        likelihood_score, confidence_tier = self._predict_with_ml(features)
                    else:
                        likelihood_score, confidence_tier = self.calculate_scoring_index(features)
                    
                    # Create prediction record
                    prediction = ReservePrediction(
                        mine_id=mine.id,
                        prediction_date=datetime.now(),
                        predicted_reserve_tonnes=float(likelihood_score * 10000),  # Placeholder scaling
                        confidence_level=float({'High': 0.9, 'Medium': 0.7, 'Low': 0.5}.get(confidence_tier, 0.5)),
                        model_version=f"reserve_targeting_v1_{self.model_type}",
                        source_tag=SourceTag.SYNTHETIC
                    )
                    self.db.add(prediction)
                    self.db.flush()
                    
                    # Create explanation record
                    try:
                        self._create_explanation(prediction.id, features, 'reserve', self.model_type)
                    except Exception as e:
                        logger.warning(f"Failed to create explanation for prediction {prediction.id}: {e}")
                    
                    predictions_created += 1
            
            self.db.commit()
            logger.info(f"Created {predictions_created} reserve predictions")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error generating predictions: {e}")
            raise
    
    def _get_cell_features(self, drillhole: Drillhole, mine_id: int) -> Dict:
        """Get features for a cell (drillhole location)"""
        # Get assay data for this drillhole
        assays = self.db.query(AssayInterval).filter(
            AssayInterval.drillhole_id == drillhole.id
        ).all()
        
        avg_grade = np.mean([a.mn_percent for a in assays if a.mn_percent]) if assays else 0
        
        # Count nearby drillholes (simplified)
        nearby_drillholes = self.db.query(func.count(Drillhole.id)).filter(
            Drillhole.mine_id == mine_id,
            Drillhole.id != drillhole.id
        ).scalar()
        
        return {
            'interpolated_grade_idw': avg_grade,
            'distance_to_nearest_drillhole': 100.0,  # Placeholder
            'drillhole_density_500m': nearby_drillholes,
            'ndvi_anomaly': 0.0,  # Would calculate from env data
            'soil_moisture_anomaly': 0.0,
            'lst_anomaly': 0.0,
        }
    
    def _predict_with_ml(self, features: Dict) -> Tuple[float, str]:
        """Predict using trained ML model"""
        try:
            # Prepare feature vector
            feature_vector = np.array([[
                features.get('interpolated_grade_idw', 0),
                0,  # fe_percent placeholder
                0,  # sio2_percent placeholder
                0,  # al2o3_percent placeholder
                100,  # total_depth_m placeholder
            ]])
            
            # Get probability
            probability = float(self.ml_model.predict_proba(feature_vector)[0][1])
            
            # Determine confidence tier
            if probability > 0.7:
                confidence_tier = 'High'
            elif probability > 0.4:
                confidence_tier = 'Medium'
            else:
                confidence_tier = 'Low'
            
            return probability, confidence_tier
            
        except Exception as e:
            logger.error(f"Error in ML prediction: {e}")
            return 0.5, 'Low'
    
    def _create_explanation(self, prediction_id: int, features: Dict, 
                           prediction_type: str, model_type: str):
        """Create feature contribution explanation"""
        try:
            if model_type == 'scoring_index':
                # Use documented weights
                for feature_name, weight in self.SCORING_WEIGHTS.items():
                    feature_value = float(features.get(feature_name, 0))
                    explanation = PredictionExplanation(
                        prediction_id=prediction_id,
                        prediction_type=prediction_type,
                        feature_name=feature_name,
                        feature_value=feature_value,
                        importance_score=float(weight),
                        direction='positive' if feature_value > 0 else 'negative',
                        source_tag=SourceTag.SYNTHETIC
                    )
                    self.db.add(explanation)
            else:
                # ML model feature importance
                if self.ml_model and hasattr(self.ml_model, 'feature_importances_'):
                    importances = self.ml_model.feature_importances_
                    feature_names = ['mn_percent', 'fe_percent', 'sio2_percent', 
                                   'al2o3_percent', 'total_depth_m']
                    
                    for i, (name, importance) in enumerate(zip(feature_names, importances)):
                        explanation = PredictionExplanation(
                            prediction_id=prediction_id,
                            prediction_type=prediction_type,
                            feature_name=name,
                            feature_value=0.0,  # Would use actual feature value
                            importance_score=float(importance),
                            direction='positive',
                            source_tag=SourceTag.SYNTHETIC
                        )
                        self.db.add(explanation)
            
        except Exception as e:
            logger.error(f"Error creating explanation: {e}")
    
    def close(self):
        """Close database connection"""
        self.db.close()


def main():
    """Main function to run reserve targeting model"""
    model = ReserveTargetingModel()
    try:
        # Check data density
        density_info = model.check_data_density()
        print(f"Data density: {density_info}")
        
        # Generate predictions
        model.generate_predictions()
        
        logger.info("Reserve targeting completed successfully")
        
    finally:
        model.close()


if __name__ == "__main__":
    main()
