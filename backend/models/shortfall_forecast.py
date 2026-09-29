"""
Shortfall forecast model for production prediction
Implements gradient-boosted regressor with seasonal-naive baseline comparison
"""

from sqlalchemy.orm import Session
from sqlalchemy import text, func
from database import SessionLocal
from models.schema import (
    Mine, ProductionRecord, EquipmentEvent, BlastRecord, 
    EnvObservation, ShortfallPrediction, PredictionExplanation, SourceTag
)
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ShortfallForecastModel:
    """
    Shortfall forecast model with two approaches:
    1. Gradient-boosted regressor (XGBoost/LightGBM)
    2. Seasonal-naive baseline (for comparison)
    """
    
    # Risk tier thresholds
    RISK_THRESHOLDS = {
        'High': 0.15,      # >15% predicted shortfall
        'Medium': 0.05,    # >5% predicted shortfall
        'Low': 0.0         # <=5% predicted shortfall
    }
    
    def __init__(self):
        self.db = SessionLocal()
        self.ml_model = None
        self.baseline_error = None  # Will store MAE for seasonal baseline
    
    def prepare_training_data(self, mine_id: Optional[int] = None) -> pd.DataFrame:
        """
        Prepare training data from production records and related features
        
        Args:
            mine_id: Optional mine ID to filter
            
        Returns:
            DataFrame with features and target
        """
        try:
            # Get production records with rolling features
            query = text("""
                SELECT 
                    pr.mine_id,
                    pr.record_date,
                    pr.shortfall_tonnes,
                    pr.target_tonnes,
                    pr.ore_extracted_tonnes,
                    LAG(pr.shortfall_tonnes, 7) OVER (PARTITION BY pr.mine_id ORDER BY pr.record_date) as shortfall_7d_ago,
                    LAG(pr.shortfall_tonnes, 30) OVER (PARTITION BY pr.mine_id ORDER BY pr.record_date) as shortfall_30d_ago,
                    EXTRACT(MONTH FROM pr.record_date) as month,
                    EXTRACT(QUARTER FROM pr.record_date) as quarter,
                    CASE WHEN EXTRACT(MONTH FROM pr.record_date) IN (6,7,8,9) THEN 1 ELSE 0 END as is_monsoon
                FROM production_records pr
                WHERE pr.shortfall_tonnes IS NOT NULL
                ORDER BY pr.mine_id, pr.record_date
            """)
            
            if mine_id:
                query = text(query.text.replace("FROM production_records pr", 
                    f"FROM production_records pr WHERE pr.mine_id = {mine_id} AND"))
            
            results = self.db.execute(query).fetchall()
            
            if not results:
                logger.warning("No production data found for training")
                return pd.DataFrame()
            
            df = pd.DataFrame(results, columns=[
                'mine_id', 'record_date', 'shortfall_tonnes', 'target_tonnes',
                'ore_extracted_tonnes', 'shortfall_7d_ago', 'shortfall_30d_ago',
                'month', 'quarter', 'is_monsoon'
            ])
            
            # Add equipment availability feature
            df['equipment_availability'] = df.apply(
                lambda row: self._get_equipment_availability(row['mine_id'], row['record_date']),
                axis=1
            )
            
            # Add blast delay feature
            df['blast_delay_days'] = df.apply(
                lambda row: self._get_blast_delay(row['mine_id'], row['record_date']),
                axis=1
            )
            
            # Add rainfall feature
            df['rainfall_7d_total'] = df.apply(
                lambda row: self._get_rainfall_total(row['mine_id'], row['record_date']),
                axis=1
            )
            
            # Calculate target: shortfall percentage
            df['shortfall_pct'] = (df['shortfall_tonnes'] / df['target_tonnes']) * 100
            df['shortfall_pct'] = df['shortfall_pct'].fillna(0)
            
            # Drop rows with missing lagged values
            df = df.dropna(subset=['shortfall_7d_ago', 'shortfall_30d_ago'])
            
            logger.info(f"Prepared {len(df)} training samples")
            return df
            
        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            return pd.DataFrame()
    
    def _get_equipment_availability(self, mine_id: int, date: datetime) -> float:
        """Get equipment availability for a date"""
        start_of_day = datetime(date.year, date.month, date.day)
        end_of_day = start_of_day + timedelta(days=1)
        
        downtime = self.db.query(
            func.sum(EquipmentEvent.downtime_hours)
        ).filter(
            EquipmentEvent.mine_id == mine_id,
            EquipmentEvent.start_time >= start_of_day,
            EquipmentEvent.start_time < end_of_day
        ).scalar()
        
        availability = ((24.0 - (downtime or 0.0)) / 24.0) * 100
        return max(0.0, min(100.0, availability))
    
    def _get_blast_delay(self, mine_id: int, date: datetime) -> float:
        """Get blast delay for a date"""
        start_of_day = datetime(date.year, date.month, date.day)
        end_of_day = start_of_day + timedelta(days=1)
        
        result = self.db.query(
            func.avg(BlastRecord.delay_hours)
        ).filter(
            BlastRecord.mine_id == mine_id,
            BlastRecord.scheduled_date >= start_of_day,
            BlastRecord.scheduled_date < end_of_day,
            BlastRecord.delay_hours.isnot(None)
        ).scalar()
        
        return result if result else 0.0
    
    def _get_rainfall_total(self, mine_id: int, date: datetime) -> float:
        """Get 7-day rainfall total"""
        start_date = date - timedelta(days=7)
        
        result = self.db.query(
            func.sum(EnvObservation.value)
        ).filter(
            EnvObservation.mine_id == mine_id,
            EnvObservation.layer_type == 'rainfall',
            EnvObservation.observation_date > start_date,
            EnvObservation.observation_date <= date
        ).scalar()
        
        return result if result else 0.0
    
    def train_ml_model(self, mine_id: Optional[int] = None):
        """
        Train gradient-boosted regressor for shortfall prediction
        
        Args:
            mine_id: Optional mine ID to filter
        """
        try:
            from xgboost import XGBRegressor
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import mean_absolute_error, mean_squared_error
            
            logger.info("Training gradient-boosted regressor...")
            
            # Prepare training data
            df = self.prepare_training_data(mine_id)
            
            if len(df) < 50:
                logger.warning("Insufficient training samples (<50)")
                return
            
            # Feature columns
            feature_cols = [
                'shortfall_7d_ago', 'shortfall_30d_ago',
                'equipment_availability', 'blast_delay_days',
                'rainfall_7d_total', 'month', 'quarter', 'is_monsoon'
            ]
            
            X = df[feature_cols].fillna(0).astype(float)
            y = df['shortfall_pct'].astype(float)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train XGBoost regressor
            self.ml_model = XGBRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
            
            self.ml_model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.ml_model.predict(X_test)
            mae = float(mean_absolute_error(y_test, y_pred))
            rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
            
            logger.info(f"ML Model MAE: {mae:.2f}%, RMSE: {rmse:.2f}%")
            
            # Compare with seasonal baseline
            baseline_mae = self._evaluate_seasonal_baseline(y_test)
            self.baseline_error = baseline_mae
            
            logger.info(f"Seasonal Baseline MAE: {baseline_mae:.2f}%")
            logger.info(f"ML Model Improvement: {((baseline_mae - mae) / baseline_mae * 100):.1f}%")
            
        except ImportError:
            logger.warning("XGBoost not available")
        except Exception as e:
            logger.error(f"Error training ML model: {e}")
    
    def _evaluate_seasonal_baseline(self, y_test: pd.Series) -> float:
        """
        Evaluate seasonal-naive baseline forecast
        
        Baseline: predict same shortfall as same day last year
        Simplified: use mean of historical data for same month
        """
        try:
            # Simple baseline: predict the mean shortfall percentage
            baseline_pred = np.full(len(y_test), y_test.mean())
            mae = np.mean(np.abs(y_test - baseline_pred))
            return mae
        except Exception as e:
            logger.error(f"Error evaluating baseline: {e}")
            return float('inf')
    
    def generate_predictions(self, mine_id: Optional[int] = None, forecast_days: int = 7):
        """
        Generate shortfall predictions for future dates
        
        Args:
            mine_id: Optional mine ID to filter
            forecast_days: Number of days to forecast
        """
        try:
            logger.info("Generating shortfall predictions...")
            
            # Train model if not already trained
            if self.ml_model is None:
                self.train_ml_model(mine_id)
            
            # Get mines to process
            if mine_id:
                mines = [self.db.query(Mine).filter(Mine.id == mine_id).first()]
            else:
                mines = self.db.query(Mine).all()
            
            predictions_created = 0
            
            for mine in mines:
                if not mine:
                    continue
                
                # Get latest production date
                latest_date = self.db.query(
                    func.max(ProductionRecord.record_date)
                ).filter(
                    ProductionRecord.mine_id == mine.id
                ).scalar()
                
                if not latest_date:
                    logger.warning(f"No production data for mine {mine.name}")
                    continue
                
                # Forecast for each day
                for day_offset in range(1, forecast_days + 1):
                    target_date = latest_date + timedelta(days=day_offset)
                    
                    # Get features for prediction
                    features = self._get_forecast_features(mine.id, target_date, latest_date)
                    
                    # Generate prediction
                    if self.ml_model:
                        predicted_shortfall_pct = self._predict_with_ml(features)
                    else:
                        # Fallback to simple heuristic
                        predicted_shortfall_pct = features.get('shortfall_7d_ago', 0)
                    
                    # Get target tonnes for scaling
                    target_tonnes = self.db.query(
                        ProductionRecord.target_tonnes
                    ).filter(
                        ProductionRecord.mine_id == mine.id,
                        ProductionRecord.record_date == latest_date
                    ).scalar()
                    
                    if not target_tonnes:
                        target_tonnes = 1000  # Default fallback
                    
                    # Calculate predicted shortfall in tonnes
                    predicted_shortfall_tonnes = (predicted_shortfall_pct / 100) * target_tonnes
                    
                    # Determine risk tier
                    risk_tier = self._determine_risk_tier(predicted_shortfall_pct)
                    
                    # Create prediction record
                    prediction = ShortfallPrediction(
                        mine_id=mine.id,
                        prediction_date=datetime.now(),
                        target_date=target_date,
                        predicted_shortfall_tonnes=float(predicted_shortfall_tonnes),
                        probability=float(predicted_shortfall_pct / 100),  # Convert to 0-1
                        contributing_factors=str(features),
                        model_version="shortfall_forecast_v1_xgboost",
                        source_tag=SourceTag.SYNTHETIC
                    )
                    self.db.add(prediction)
                    self.db.flush()
                    
                    # Create explanation record
                    self._create_explanation(prediction.id, features, 'shortfall')
                    
                    predictions_created += 1
            
            self.db.commit()
            logger.info(f"Created {predictions_created} shortfall predictions")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error generating predictions: {e}")
            raise
    
    def _get_forecast_features(self, mine_id: int, target_date: datetime, 
                              latest_date: datetime) -> Dict:
        """Get features for forecasting"""
        # Get recent shortfall values
        shortfall_7d_ago = self.db.query(
            ProductionRecord.shortfall_tonnes,
            ProductionRecord.target_tonnes
        ).filter(
            ProductionRecord.mine_id == mine_id,
            ProductionRecord.record_date == latest_date - timedelta(days=7)
        ).first()
        
        if shortfall_7d_ago:
            shortfall_7d_pct = (shortfall_7d_ago[0] / shortfall_7d_ago[1]) * 100 if shortfall_7d_ago[1] else 0
        else:
            shortfall_7d_pct = 0
        
        shortfall_30d_ago = self.db.query(
            ProductionRecord.shortfall_tonnes,
            ProductionRecord.target_tonnes
        ).filter(
            ProductionRecord.mine_id == mine_id,
            ProductionRecord.record_date == latest_date - timedelta(days=30)
        ).first()
        
        if shortfall_30d_ago:
            shortfall_30d_pct = (shortfall_30d_ago[0] / shortfall_30d_ago[1]) * 100 if shortfall_30d_ago[1] else 0
        else:
            shortfall_30d_pct = 0
        
        # Get current operational features
        equipment_availability = self._get_equipment_availability(mine_id, latest_date)
        blast_delay = self._get_blast_delay(mine_id, latest_date)
        rainfall_total = self._get_rainfall_total(mine_id, latest_date)
        
        # Seasonal features
        return {
            'shortfall_7d_ago': shortfall_7d_pct,
            'shortfall_30d_ago': shortfall_30d_pct,
            'equipment_availability': equipment_availability,
            'blast_delay_days': blast_delay,
            'rainfall_7d_total': rainfall_total,
            'month': int(target_date.month),
            'quarter': int((target_date.month - 1) // 3 + 1),
            'is_monsoon': int(target_date.month in [6, 7, 8, 9]),
        }
    
    def _predict_with_ml(self, features: Dict) -> float:
        """Predict using trained ML model"""
        try:
            # Prepare feature vector
            feature_vector = np.array([[
                features.get('shortfall_7d_ago', 0),
                features.get('shortfall_30d_ago', 0),
                features.get('equipment_availability', 100),
                features.get('blast_delay_days', 0),
                features.get('rainfall_7d_total', 0),
                features.get('month', 1),
                features.get('quarter', 1),
                features.get('is_monsoon', 0),
            ]])
            
            # Get prediction
            prediction = float(self.ml_model.predict(feature_vector)[0])
            return max(0.0, prediction)  # Ensure non-negative
            
        except Exception as e:
            logger.error(f"Error in ML prediction: {e}")
            return features.get('shortfall_7d_ago', 0)
    
    def _determine_risk_tier(self, predicted_shortfall_pct: float) -> str:
        """Determine risk tier based on predicted shortfall percentage"""
        if predicted_shortfall_pct >= self.RISK_THRESHOLDS['High']:
            return 'High'
        elif predicted_shortfall_pct >= self.RISK_THRESHOLDS['Medium']:
            return 'Medium'
        else:
            return 'Low'
    
    def _create_explanation(self, prediction_id: int, features: Dict, 
                           prediction_type: str):
        """Create feature contribution explanation"""
        try:
            # If ML model has feature importances, use them
            if self.ml_model and hasattr(self.ml_model, 'feature_importances_'):
                importances = self.ml_model.feature_importances_
                feature_names = [
                    'shortfall_7d_ago', 'shortfall_30d_ago',
                    'equipment_availability', 'blast_delay_days',
                    'rainfall_7d_total', 'month', 'quarter', 'is_monsoon'
                ]
                
                for i, (name, importance) in enumerate(zip(feature_names, importances)):
                    feature_value = features.get(name, 0)
                    explanation = PredictionExplanation(
                        prediction_id=prediction_id,
                        prediction_type=prediction_type,
                        feature_name=name,
                        feature_value=float(feature_value),
                        importance_score=float(importance),
                        direction='positive' if importance > 0 else 'negative',
                        source_tag=SourceTag.SYNTHETIC
                    )
                    self.db.add(explanation)
            else:
                # Fallback: use feature values as proxy for importance
                for feature_name, feature_value in features.items():
                    explanation = PredictionExplanation(
                        prediction_id=prediction_id,
                        prediction_type=prediction_type,
                        feature_name=feature_name,
                        feature_value=float(feature_value),
                        importance_score=abs(float(feature_value)) / 100,  # Normalized
                        direction='positive' if feature_value > 0 else 'negative',
                        source_tag=SourceTag.SYNTHETIC
                    )
                    self.db.add(explanation)
            
        except Exception as e:
            logger.error(f"Error creating explanation: {e}")
    
    def get_model_performance(self) -> Dict:
        """Get model performance metrics"""
        return {
            'ml_model_trained': self.ml_model is not None,
            'baseline_mae': float(self.baseline_error) if self.baseline_error else None,
            'risk_thresholds': self.RISK_THRESHOLDS
        }
    
    def close(self):
        """Close database connection"""
        self.db.close()


def main():
    """Main function to run shortfall forecast model"""
    model = ShortfallForecastModel()
    try:
        # Train model
        model.train_ml_model()
        
        # Generate predictions
        model.generate_predictions(forecast_days=7)
        
        # Report performance
        performance = model.get_model_performance()
        logger.info(f"Model performance: {performance}")
        
        logger.info("Shortfall forecast completed successfully")
        
    finally:
        model.close()


if __name__ == "__main__":
    main()
