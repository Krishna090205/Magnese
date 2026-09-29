"""
Batch scoring script for shortfall forecast
Re-runnable, idempotent, and logged
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processing.feature_engineering import FeatureEngineer
from models.shortfall_forecast import ShortfallForecastModel
from processing.decision_logic import DecisionEngine
from database import SessionLocal
from models.schema import ShortfallPrediction, PredictionExplanation, Recommendation
from sqlalchemy import text
from datetime import datetime
import logging
import argparse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_logging(log_file: str = None):
    """Setup logging to file if specified"""
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)


def clear_previous_predictions(mine_id: int = None):
    """
    Clear previous predictions for idempotency
    
    Args:
        mine_id: Optional mine ID to filter (None = all mines)
    """
    try:
        db = SessionLocal()
        
        # Delete recommendations first (dependent on predictions)
        delete_recommendations = text("""
            DELETE FROM recommendations 
            WHERE id IN (
                SELECT recommendation_id FROM actions_log
                WHERE action_type = 'recommendation_generated'
            )
        """)
        
        # Delete action logs
        delete_actions = text("DELETE FROM actions_log")
        db.execute(delete_actions)
        
        # Delete explanations first (due to foreign key)
        delete_explanations = text("""
            DELETE FROM prediction_explanations 
            WHERE prediction_id IN (
                SELECT id FROM shortfall_predictions
                WHERE prediction_date >= :today
            )
        """)
        
        params = {'today': datetime.now().date()}
        
        if mine_id:
            delete_explanations = text(delete_explanations.text.replace(
                "WHERE prediction_date >= :today",
                f"WHERE prediction_id IN (SELECT id FROM shortfall_predictions WHERE mine_id = {mine_id} AND prediction_date >= :today)"
            ))
        
        db.execute(delete_explanations, params)
        
        # Delete predictions
        delete_predictions = text("""
            DELETE FROM shortfall_predictions 
            WHERE prediction_date >= :today
        """)
        
        if mine_id:
            delete_predictions = text(delete_predictions.text.replace(
                "WHERE prediction_date >= :today",
                f"WHERE mine_id = {mine_id} AND prediction_date >= :today"
            ))
        
        result = db.execute(delete_predictions, params)
        deleted_count = result.rowcount
        
        db.commit()
        db.close()
        
        logger.info(f"Cleared {deleted_count} previous shortfall predictions")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error clearing previous predictions: {e}")
        raise


def run_shortfall_scoring(mine_id: int = None, forecast_days: int = 7, 
                         skip_clear: bool = False, generate_recommendations: bool = True):
    """
    Run shortfall forecast batch scoring
    
    Args:
        mine_id: Optional mine ID to filter (None = all mines)
        forecast_days: Number of days to forecast
        skip_clear: Skip clearing previous predictions (for testing)
        generate_recommendations: Whether to generate recommendations
    """
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("Starting Shortfall Forecast Batch Scoring")
    logger.info(f"Mine ID filter: {mine_id if mine_id else 'All mines'}")
    logger.info(f"Forecast days: {forecast_days}")
    logger.info(f"Skip clear: {skip_clear}")
    logger.info(f"Generate recommendations: {generate_recommendations}")
    logger.info("=" * 60)
    
    try:
        # Clear previous predictions for idempotency
        if not skip_clear:
            clear_previous_predictions(mine_id)
        
        # Step 1: Feature engineering
        logger.info("Step 1: Running feature engineering...")
        feature_engineer = FeatureEngineer()
        try:
            feature_engineer.create_mine_day_features(lookback_days=30)
        finally:
            feature_engineer.close()
        
        # Step 2: Generate predictions
        logger.info("Step 2: Generating shortfall predictions...")
        model = ShortfallForecastModel()
        try:
            # Train model
            model.train_ml_model(mine_id=mine_id)
            
            # Generate predictions
            model.generate_predictions(mine_id=mine_id, forecast_days=forecast_days)
            
            # Report model performance
            performance = model.get_model_performance()
            logger.info(f"Model performance: {performance}")
            
        finally:
            model.close()
        
        # Step 3: Generate recommendations
        recommendations_created = 0
        if generate_recommendations:
            logger.info("Step 3: Generating recommendations...")
            decision_engine = DecisionEngine()
            try:
                decision_engine.generate_recommendations(mine_id=mine_id, risk_threshold='Medium')
                
                # Count recommendations
                db = SessionLocal()
                try:
                    query = db.query(Recommendation)
                    if mine_id:
                        query = query.filter(Recommendation.mine_id == mine_id)
                    recommendations_created = query.count()
                finally:
                    db.close()
                
            finally:
                decision_engine.close()
        
        # Step 4: Verify results
        logger.info("Step 4: Verifying results...")
        db = SessionLocal()
        try:
            query = db.query(ShortfallPrediction)
            if mine_id:
                query = query.filter(ShortfallPrediction.mine_id == mine_id)
            
            predictions = query.filter(
                ShortfallPrediction.prediction_date >= datetime.now().date()
            ).count()
            
            logger.info(f"Generated {predictions} shortfall predictions")
            
            # Check explanations
            explanations = db.query(PredictionExplanation).filter(
                PredictionExplanation.prediction_type == 'shortfall'
            ).count()
            
            logger.info(f"Generated {explanations} prediction explanations")
            logger.info(f"Generated {recommendations_created} recommendations")
            
        finally:
            db.close()
        
        # Report completion
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 60)
        logger.info("Shortfall Forecast Batch Scoring Completed Successfully")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Predictions generated: {predictions}")
        logger.info(f"Explanations generated: {explanations}")
        logger.info(f"Recommendations generated: {recommendations_created}")
        logger.info("=" * 60)
        
        return {
            'status': 'success',
            'duration_seconds': duration,
            'predictions_generated': predictions,
            'explanations_generated': explanations,
            'recommendations_generated': recommendations_created,
            'model_performance': performance
        }
        
    except Exception as e:
        logger.error(f"Batch scoring failed: {e}")
        raise


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Batch scoring script for shortfall forecast'
    )
    parser.add_argument(
        '--mine-id',
        type=int,
        help='Filter by specific mine ID (default: all mines)'
    )
    parser.add_argument(
        '--forecast-days',
        type=int,
        default=7,
        help='Number of days to forecast (default: 7)'
    )
    parser.add_argument(
        '--skip-clear',
        action='store_true',
        help='Skip clearing previous predictions (for testing)'
    )
    parser.add_argument(
        '--no-recommendations',
        action='store_true',
        help='Skip generating recommendations'
    )
    parser.add_argument(
        '--log-file',
        type=str,
        help='Log file path (default: stdout only)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_file)
    
    # Run scoring
    try:
        result = run_shortfall_scoring(
            mine_id=args.mine_id,
            forecast_days=args.forecast_days,
            skip_clear=args.skip_clear,
            generate_recommendations=not args.no_recommendations
        )
        logger.info(f"Result: {result}")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
