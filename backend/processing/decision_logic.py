"""
Decision logic engine for generating recommendations
Maps shortfall prediction explanations to corrective actions
"""

from sqlalchemy.orm import Session
from sqlalchemy import text, func
from database import SessionLocal
from models.schema import (
    ShortfallPrediction, PredictionExplanation, Recommendation, 
    ActionLog, SourceTag
)
from datetime import datetime
from typing import Dict, List, Optional
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DecisionEngine:
    """
    Decision logic engine for generating recommendations based on
    shortfall prediction explanations
    """
    
    # Recommendation templates based on dominant contributing factors
    RECOMMENDATION_TEMPLATES = {
        'equipment_downtime': {
            'type': 'maintenance',
            'priority': 'high',
            'title': 'Equipment Maintenance Required',
            'description': 'High equipment downtime detected as primary factor for production shortfall',
            'action_items': [
                'Schedule immediate maintenance for affected equipment',
                'Review equipment maintenance logs for recurring issues',
                'Consider equipment redeployment from lower-priority areas',
                'Increase preventive maintenance frequency',
                'Evaluate backup equipment availability'
            ],
            'expected_impact': 'Reduce downtime by 15-30%, improve production availability'
        },
        'blast_delay': {
            'type': 'production',
            'priority': 'medium',
            'title': 'Blast Schedule Optimization Needed',
            'description': 'Blast delays are impacting production schedule',
            'action_items': [
                'Review blast scheduling process and identify bottlenecks',
                'Optimize explosive logistics and storage',
                'Coordinate with regulatory agencies for permit processing',
                'Implement buffer time in blast schedule',
                'Consider alternative excavation methods where feasible'
            ],
            'expected_impact': 'Reduce blast delays by 20-40%, improve schedule adherence'
        },
        'weather_rainfall': {
            'type': 'production',
            'priority': 'medium',
            'title': 'Weather-Related Schedule Adjustment',
            'description': 'High rainfall impacting mining operations',
            'action_items': [
                'Review seasonal weather patterns and adjust production targets',
                'Implement water management systems for drainage',
                'Plan alternative work for high-rainfall periods',
                'Schedule critical operations during dry windows',
                'Consider covered storage for ore and equipment'
            ],
            'expected_impact': 'Mitigate weather-related delays by 25-50%'
        },
        'seasonal_monsoon': {
            'type': 'production',
            'priority': 'high',
            'title': 'Monsoon Season Production Planning',
            'description': 'Monsoon season requires production schedule adjustments',
            'action_items': [
                'Develop monsoon-specific production plan',
                'Pre-position critical supplies before monsoon onset',
                'Strengthen site drainage and erosion control',
                'Review and reinforce road access routes',
                'Plan workforce allocation for reduced operational windows'
            ],
            'expected_impact': 'Maintain 60-80% of normal production during monsoon'
        },
        'general_shortfall': {
            'type': 'production',
            'priority': 'low',
            'title': 'Production Shortfall Review',
            'description': 'General production shortfall detected',
            'action_items': [
                'Conduct comprehensive production audit',
                'Review operational efficiency metrics',
                'Assess resource allocation and utilization',
                'Evaluate training needs for operational staff',
                'Consider process optimization opportunities'
            ],
            'expected_impact': 'Identify improvement opportunities across operations'
        }
    }
    
    # Feature to recommendation mapping
    FEATURE_TO_RECOMMENDATION = {
        'equipment_availability': 'equipment_downtime',
        'blast_delay_days': 'blast_delay',
        'rainfall_7d_total': 'weather_rainfall',
        'is_monsoon': 'seasonal_monsoon',
    }
    
    def __init__(self):
        self.db = SessionLocal()
    
    def generate_recommendations(self, mine_id: Optional[int] = None, 
                                 risk_threshold: str = 'Medium'):
        """
        Generate recommendations for shortfall predictions above risk threshold
        
        Args:
            mine_id: Optional mine ID to filter
            risk_threshold: Minimum risk tier to generate recommendations (Low/Medium/High)
        """
        try:
            logger.info(f"Generating recommendations (risk threshold: {risk_threshold})...")
            
            # Get shortfall predictions above threshold
            # For now, we'll get recent predictions
            query = self.db.query(ShortfallPrediction).filter(
                ShortfallPrediction.probability >= 0.05  # 5% shortfall threshold
            )
            
            if mine_id:
                query = query.filter(ShortfallPrediction.mine_id == mine_id)
            
            predictions = query.order_by(ShortfallPrediction.prediction_date.desc()).limit(100).all()
            
            if not predictions:
                logger.info("No predictions above threshold found")
                return
            
            recommendations_created = 0
            
            for prediction in predictions:
                # Get explanations for this prediction
                explanations = self.db.query(PredictionExplanation).filter(
                    PredictionExplanation.prediction_id == prediction.id,
                    PredictionExplanation.prediction_type == 'shortfall'
                ).all()
                
                if not explanations:
                    logger.warning(f"No explanations for prediction {prediction.id}")
                    continue
                
                # Identify dominant contributing factor
                dominant_factor = self._identify_dominant_factor(explanations)
                
                # Get recommendation template
                template_key = self.FEATURE_TO_RECOMMENDATION.get(
                    dominant_factor, 'general_shortfall'
                )
                template = self.RECOMMENDATION_TEMPLATES.get(template_key)
                
                if not template:
                    template = self.RECOMMENDATION_TEMPLATES['general_shortfall']
                
                # Create recommendation
                recommendation = Recommendation(
                    mine_id=prediction.mine_id,
                    recommendation_type=template['type'],
                    priority=template['priority'],
                    title=template['title'],
                    description=template['description'],
                    action_items=json.dumps(template['action_items']),
                    expected_impact=template['expected_impact'],
                    source_tag=SourceTag.SYNTHETIC
                )
                self.db.add(recommendation)
                self.db.flush()
                
                # Link to prediction (would add foreign key in schema)
                # For now, store in action log
                self._log_recommendation_generation(
                    recommendation.id, prediction.id, dominant_factor
                )
                
                recommendations_created += 1
            
            self.db.commit()
            logger.info(f"Created {recommendations_created} recommendations")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error generating recommendations: {e}")
            raise
    
    def _identify_dominant_factor(self, explanations: List[PredictionExplanation]) -> str:
        """
        Identify the dominant contributing factor from explanations
        
        Args:
            explanations: List of prediction explanations
            
        Returns:
            Feature name with highest importance score
        """
        if not explanations:
            return 'general_shortfall'
        
        # Sort by importance score
        sorted_explanations = sorted(
            explanations, 
            key=lambda x: x.importance_score or 0, 
            reverse=True
        )
        
        dominant = sorted_explanations[0]
        return dominant.feature_name
    
    def _log_recommendation_generation(self, recommendation_id: int, 
                                      prediction_id: int, factor: str):
        """Log recommendation generation to action log"""
        try:
            action_log = ActionLog(
                recommendation_id=recommendation_id,
                action_type='recommendation_generated',
                description=f'Recommendation generated based on shortfall prediction {prediction_id}, dominant factor: {factor}',
                performed_by='decision_engine',
                outcome='pending',
                source_tag=SourceTag.SYNTHETIC
            )
            self.db.add(action_log)
        except Exception as e:
            logger.error(f"Error logging recommendation: {e}")
    
    def get_recommendations(self, mine_id: Optional[int] = None, 
                          status: Optional[str] = None) -> List[Dict]:
        """
        Get recommendations with optional filters
        
        Args:
            mine_id: Optional mine ID to filter
            status: Optional status filter (pending, in_progress, completed, dismissed)
            
        Returns:
            List of recommendation dictionaries
        """
        try:
            query = self.db.query(Recommendation)
            
            if mine_id:
                query = query.filter(Recommendation.mine_id == mine_id)
            if status:
                query = query.filter(Recommendation.status == status)
            
            recommendations = query.order_by(
                Recommendation.generated_at.desc()
            ).limit(50).all()
            
            result = []
            for rec in recommendations:
                result.append({
                    'id': rec.id,
                    'mine_id': rec.mine_id,
                    'type': rec.recommendation_type,
                    'priority': rec.priority,
                    'title': rec.title,
                    'description': rec.description,
                    'action_items': json.loads(rec.action_items) if rec.action_items else [],
                    'expected_impact': rec.expected_impact,
                    'status': rec.status,
                    'generated_at': rec.generated_at.isoformat() if rec.generated_at else None,
                    'source_tag': rec.source_tag.value if rec.source_tag else None
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return []
    
    def update_recommendation_status(self, recommendation_id: int, 
                                    status: str, performed_by: str = None):
        """
        Update recommendation status
        
        Args:
            recommendation_id: ID of recommendation to update
            status: New status (pending, in_progress, completed, dismissed)
            performed_by: User or system performing the update
        """
        try:
            recommendation = self.db.query(Recommendation).filter(
                Recommendation.id == recommendation_id
            ).first()
            
            if not recommendation:
                logger.warning(f"Recommendation {recommendation_id} not found")
                return
            
            old_status = recommendation.status
            recommendation.status = status
            
            # Log the status change
            action_log = ActionLog(
                recommendation_id=recommendation_id,
                action_type='status_update',
                description=f'Status changed from {old_status} to {status}',
                performed_by=performed_by or 'system',
                outcome=status,
                source_tag=SourceTag.SYNTHETIC
            )
            self.db.add(action_log)
            
            self.db.commit()
            logger.info(f"Updated recommendation {recommendation_id} status to {status}")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating recommendation status: {e}")
            raise
    
    def get_action_history(self, recommendation_id: int) -> List[Dict]:
        """
        Get action history for a recommendation
        
        Args:
            recommendation_id: ID of recommendation
            
        Returns:
            List of action log entries
        """
        try:
            actions = self.db.query(ActionLog).filter(
                ActionLog.recommendation_id == recommendation_id
            ).order_by(ActionLog.performed_at.desc()).all()
            
            result = []
            for action in actions:
                result.append({
                    'id': action.id,
                    'action_type': action.action_type,
                    'description': action.description,
                    'performed_by': action.performed_by,
                    'performed_at': action.performed_at.isoformat() if action.performed_at else None,
                    'outcome': action.outcome,
                    'source_tag': action.source_tag.value if action.source_tag else None
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting action history: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        self.db.close()


def main():
    """Main function to run decision engine"""
    engine = DecisionEngine()
    try:
        # Generate recommendations for all mines
        engine.generate_recommendations(risk_threshold='Medium')
        
        # Get and display recommendations
        recommendations = engine.get_recommendations()
        logger.info(f"Generated {len(recommendations)} recommendations")
        
        for rec in recommendations[:5]:  # Show first 5
            logger.info(f"\nRecommendation: {rec['title']}")
            logger.info(f"Priority: {rec['priority']}")
            logger.info(f"Type: {rec['type']}")
        
        logger.info("Decision engine completed successfully")
        
    finally:
        engine.close()


if __name__ == "__main__":
    main()
