"""
Synthetic production data generator
Generates structurally realistic production data correlated with weather patterns
"""

from sqlalchemy.orm import Session
from database import SessionLocal
from models.schema import Mine, ProductionRecord, SourceTag, EnvObservation
from datetime import datetime, timedelta
import random
import numpy as np


def generate_synthetic_production_data(years: int = 2):
    """Generate synthetic production data correlated with weather"""
    print(f"Generating synthetic production data for {years} years")
    
    db = SessionLocal()
    try:
        mines = db.query(Mine).all()
        if not mines:
            print("No mines found in database")
            return
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365*years)
        
        records_added = 0
        current_date = start_date
        
        while current_date <= end_date:
            for mine in mines:
                # Get rainfall data for this date if available
                rainfall_obs = db.query(EnvObservation).filter(
                    EnvObservation.mine_id == mine.id,
                    EnvObservation.observation_date == current_date.date(),
                    EnvObservation.layer_type == 'rainfall'
                ).first()
                
                # Base production on mine capacity
                daily_capacity = mine.capacity_tonnes_per_year / 365 if mine.capacity_tonnes_per_year else 1000
                
                # Adjust for rainfall (high rainfall reduces production)
                if rainfall_obs and rainfall_obs.value > 50:  # Heavy rainfall day
                    production_factor = random.uniform(0.3, 0.6)
                elif rainfall_obs and rainfall_obs.value > 20:  # Moderate rainfall
                    production_factor = random.uniform(0.7, 0.9)
                else:  # Normal day
                    production_factor = random.uniform(0.85, 1.1)
                
                # Seasonal variation (monsoon reduces production)
                month = current_date.month
                if 6 <= month <= 9:  # Monsoon season
                    production_factor *= random.uniform(0.7, 0.9)
                
                ore_extracted = daily_capacity * production_factor
                mn_grade = random.uniform(25, 45)  # 25-45% Mn grade
                mn_content = ore_extracted * (mn_grade / 100)
                
                # Target production with some shortfall
                target_tonnes = daily_capacity
                shortfall_tonnes = max(0, target_tonnes - ore_extracted)
                
                production = ProductionRecord(
                    mine_id=mine.id,
                    record_date=current_date.date(),
                    ore_extracted_tonnes=ore_extracted,
                    mn_content_tonnes=mn_content,
                    grade_percent=mn_grade,
                    target_tonnes=target_tonnes,
                    shortfall_tonnes=shortfall_tonnes,
                    source_tag=SourceTag.SYNTHETIC
                )
                db.add(production)
                records_added += 1
            
            current_date += timedelta(days=1)
        
        db.commit()
        print(f"Added {records_added} synthetic production records")
        
    except Exception as e:
        db.rollback()
        print(f"Error generating synthetic production data: {e}")
    finally:
        db.close()


def main():
    """Main function to generate synthetic production data"""
    generate_synthetic_production_data(years=2)


if __name__ == "__main__":
    main()
