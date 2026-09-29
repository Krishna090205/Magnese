"""
Synthetic rainfall data generator as fallback for CHIRPS
Generates structurally realistic rainfall data correlated with monsoon patterns
"""

from sqlalchemy.orm import Session
from database import SessionLocal
from models.schema import Mine, EnvObservation, SourceTag
from datetime import datetime, timedelta
import random
import numpy as np


def generate_synthetic_rainfall_data(years: int = 1):
    """Generate synthetic rainfall data correlated with monsoon patterns"""
    print(f"Generating synthetic rainfall data for {years} years")
    
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
                # Generate rainfall based on monsoon patterns
                month = current_date.month
                day = current_date.day
                
                # Monsoon season (June-September) - high rainfall
                if 6 <= month <= 9:
                    if month == 7 or month == 8:  # Peak monsoon
                        if random.random() < 0.7:  # 70% chance of rain
                            rainfall = random.uniform(10, 100)  # 10-100mm
                        else:
                            rainfall = random.uniform(0, 5)  # Light rain
                    else:  # June/September - moderate monsoon
                        if random.random() < 0.5:  # 50% chance of rain
                            rainfall = random.uniform(5, 50)  # 5-50mm
                        else:
                            rainfall = random.uniform(0, 3)  # Light rain
                # Pre-monsoon (March-May) - occasional thunderstorms
                elif 3 <= month <= 5:
                    if random.random() < 0.2:  # 20% chance of rain
                        rainfall = random.uniform(5, 30)  # 5-30mm
                    else:
                        rainfall = 0
                # Post-monsoon (October-November) - retreating monsoon
                elif 10 <= month <= 11:
                    if random.random() < 0.3:  # 30% chance of rain
                        rainfall = random.uniform(5, 40)  # 5-40mm
                    else:
                        rainfall = random.uniform(0, 2)  # Light rain
                # Winter (December-February) - dry season
                else:
                    if random.random() < 0.05:  # 5% chance of light rain
                        rainfall = random.uniform(0, 5)  # 0-5mm
                    else:
                        rainfall = 0
                
                obs = EnvObservation(
                    mine_id=mine.id,
                    observation_date=current_date.date(),
                    layer_type='rainfall',
                    value=rainfall,
                    unit='mm/day',
                    source_tag=SourceTag.SYNTHETIC
                )
                db.add(obs)
                records_added += 1
            
            current_date += timedelta(days=1)
        
        db.commit()
        print(f"Added {records_added} synthetic rainfall records")
        
    except Exception as e:
        db.rollback()
        print(f"Error generating synthetic rainfall data: {e}")
    finally:
        db.close()


def main():
    """Main function to generate synthetic rainfall data"""
    generate_synthetic_rainfall_data(years=1)


if __name__ == "__main__":
    main()
