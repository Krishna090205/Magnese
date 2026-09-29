"""
Batch scoring script for reserve targeting
Re-runnable, idempotent, and logged
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processing.feature_engineering import FeatureEngineer
from models.reserve_targeting import ReserveTargetingModel
from database import SessionLocal
from models.schema import ReservePrediction, PredictionExplanation
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
        
        # Delete explanations first (due to foreign key)
        delete_explanations = text("""
            DELETE FROM prediction_explanations 
            WHERE prediction_id IN (
                SELECT id FROM reserve_predictions
                WHERE prediction_date >= :today
            )
        """)
        
        params = {'today': datetime.now().date()}
        
        if mine_id:
            delete_explanations = text(delete_explanations.text.replace(
                "WHERE prediction_date >= :today",
                f"WHERE prediction_id IN (SELECT id FROM reserve_predictions WHERE mine_id = {mine_id} AND prediction_date >= :today)"
            ))
        
        db.execute(delete_explanations, params)
        
        # Delete predictions
        delete_predictions = text("""
            DELETE FROM reserve_predictions 
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
        
        logger.info(f"Cleared {deleted_count} previous reserve predictions")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error clearing previous predictions: {e}")
        raise


def run_reserve_scoring(mine_id: int = None, skip_clear: bool = False):
    """
    Run reserve targeting batch scoring
    
    Args:
        mine_id: Optional mine ID to filter (None = all mines)
        skip_clear: Skip clearing previous predictions (for testing)
    """
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("Starting Reserve Targeting Batch Scoring")
    logger.info(f"Mine ID filter: {mine_id if mine_id else 'All mines'}")
    logger.info(f"Skip clear: {skip_clear}")
    logger.info("=" * 60)
    
    try:
        # Clear previous predictions for idempotency
        if not skip_clear:
            clear_previous_predictions(mine_id)
        
        # Step 1: Feature engineering
        logger.info("Step 1: Running feature engineering...")
        feature_engineer = FeatureEngineer()
        try:
            feature_engineer.create_mine_cell_features(grid_resolution_m=100.0)
        finally:
            feature_engineer.close()
        
        # Step 2: Generate predictions
        logger.info("Step 2: Generating reserve predictions...")
        model = ReserveTargetingModel()
        try:
            # Check data density
            density_info = model.check_data_density()
            logger.info(f"Data density check: {density_info}")
            
            # Generate predictions
            model.generate_predictions(mine_id=mine_id)
            
            # Report model type used
            logger.info(f"Model type used: {model.model_type}")
            
        finally:
            model.close()
        
        # Step 3: Verify results
        logger.info("Step 3: Verifying results...")
        db = SessionLocal()
        try:
            query = db.query(ReservePrediction)
            if mine_id:
                query = query.filter(ReservePrediction.mine_id == mine_id)
            
            predictions = query.filter(
                ReservePrediction.prediction_date >= datetime.now().date()
            ).count()
            
            logger.info(f"Generated {predictions} reserve predictions")
            
            # Check explanations
            explanations = db.query(PredictionExplanation).filter(
                PredictionExplanation.prediction_type == 'reserve'
            ).count()
            
            logger.info(f"Generated {explanations} prediction explanations")
            
        finally:
            db.close()
        
        # Report completion
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 60)
        logger.info("Reserve Targeting Batch Scoring Completed Successfully")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Predictions generated: {predictions}")
        logger.info(f"Explanations generated: {explanations}")
        logger.info("=" * 60)
        
        return {
            'status': 'success',
            'duration_seconds': duration,
            'predictions_generated': predictions,
            'explanations_generated': explanations,
            'model_type': model.model_type
        }
        
    except Exception as e:
        logger.error(f"Batch scoring failed: {e}")
        raise


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Batch scoring script for reserve targeting'
    )
    parser.add_argument(
        '--mine-id',
        type=int,
        help='Filter by specific mine ID (default: all mines)'
    )
    parser.add_argument(
        '--skip-clear',
        action='store_true',
        help='Skip clearing previous predictions (for testing)'
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
        result = run_reserve_scoring(
            mine_id=args.mine_id,
            skip_clear=args.skip_clear
        )
        logger.info(f"Result: {result}")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
