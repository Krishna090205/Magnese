"""
Master batch scoring script - runs both reserve and shortfall scoring
Re-runnable, idempotent, and logged
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.score_reserve_targets import run_reserve_scoring
from scripts.score_shortfall_forecast import run_shortfall_scoring
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


def run_all_scoring(mine_id: int = None, forecast_days: int = 7, 
                   skip_clear: bool = False, generate_recommendations: bool = True):
    """
    Run all batch scoring jobs
    
    Args:
        mine_id: Optional mine ID to filter (None = all mines)
        forecast_days: Number of days to forecast
        skip_clear: Skip clearing previous predictions (for testing)
        generate_recommendations: Whether to generate recommendations
    """
    start_time = datetime.now()
    logger.info("=" * 80)
    logger.info("STARTING ALL BATCH SCORING JOBS")
    logger.info(f"Timestamp: {start_time.isoformat()}")
    logger.info(f"Mine ID filter: {mine_id if mine_id else 'All mines'}")
    logger.info(f"Forecast days: {forecast_days}")
    logger.info(f"Skip clear: {skip_clear}")
    logger.info(f"Generate recommendations: {generate_recommendations}")
    logger.info("=" * 80)
    
    results = {}
    
    try:
        # Run reserve targeting scoring
        logger.info("\n" + "=" * 80)
        logger.info("JOB 1: RESERVE TARGETING SCORING")
        logger.info("=" * 80)
        
        try:
            results['reserve'] = run_reserve_scoring(
                mine_id=mine_id,
                skip_clear=skip_clear
            )
            logger.info(f"Reserve scoring completed: {results['reserve']}")
        except Exception as e:
            logger.error(f"Reserve scoring failed: {e}")
            results['reserve'] = {'status': 'failed', 'error': str(e)}
        
        # Run shortfall forecast scoring
        logger.info("\n" + "=" * 80)
        logger.info("JOB 2: SHORTFALL FORECAST SCORING")
        logger.info("=" * 80)
        
        try:
            results['shortfall'] = run_shortfall_scoring(
                mine_id=mine_id,
                forecast_days=forecast_days,
                skip_clear=skip_clear,
                generate_recommendations=generate_recommendations
            )
            logger.info(f"Shortfall scoring completed: {results['shortfall']}")
        except Exception as e:
            logger.error(f"Shortfall scoring failed: {e}")
            results['shortfall'] = {'status': 'failed', 'error': str(e)}
        
        # Final summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("\n" + "=" * 80)
        logger.info("ALL BATCH SCORING JOBS COMPLETED")
        logger.info(f"Total duration: {duration:.2f} seconds")
        logger.info("=" * 80)
        
        logger.info("\nSUMMARY:")
        logger.info(f"Reserve targeting: {results.get('reserve', {}).get('status', 'unknown')}")
        logger.info(f"Shortfall forecast: {results.get('shortfall', {}).get('status', 'unknown')}")
        
        if results.get('reserve', {}).get('status') == 'success':
            logger.info(f"  - Predictions: {results['reserve'].get('predictions_generated', 0)}")
            logger.info(f"  - Explanations: {results['reserve'].get('explanations_generated', 0)}")
            logger.info(f"  - Model type: {results['reserve'].get('model_type', 'unknown')}")
        
        if results.get('shortfall', {}).get('status') == 'success':
            logger.info(f"  - Predictions: {results['shortfall'].get('predictions_generated', 0)}")
            logger.info(f"  - Explanations: {results['shortfall'].get('explanations_generated', 0)}")
            logger.info(f"  - Recommendations: {results['shortfall'].get('recommendations_generated', 0)}")
        
        # Check if all jobs succeeded
        all_success = all(
            r.get('status') == 'success' for r in results.values()
        )
        
        if all_success:
            logger.info("\n✓ All scoring jobs completed successfully")
            return results
        else:
            logger.warning("\n⚠ Some scoring jobs failed")
            return results
        
    except Exception as e:
        logger.error(f"Fatal error in batch scoring: {e}")
        raise


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Master batch scoring script - runs both reserve and shortfall scoring'
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
    
    # Run all scoring
    try:
        result = run_all_scoring(
            mine_id=args.mine_id,
            forecast_days=args.forecast_days,
            skip_clear=args.skip_clear,
            generate_recommendations=not args.no_recommendations
        )
        
        # Exit with error if any job failed
        all_success = all(
            r.get('status') == 'success' for r in result.values()
        )
        
        sys.exit(0 if all_success else 1)
        
    except Exception as e:
        logger.error(f"Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
