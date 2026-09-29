"""
Synthetic blast record data generator
Generates structurally realistic blasting delay records correlated with weather
"""

from sqlalchemy.orm import Session
from database import SessionLocal
from models.schema import Mine, BlastRecord, SourceTag
from datetime import datetime, timedelta
import random


def generate_synthetic_blast_data(years: int = 2):
    """Generate synthetic blast record data correlated with weather"""
    print(f"Generating synthetic blast record data for {years} years")
    
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
                # Blasts typically happen 2-3 times per week
                if random.random() < 0.35:  # ~35% chance of blast on any given day
                    scheduled_time = current_date + timedelta(hours=random.randint(10, 14))
                    
                    # Simulate rainfall effects based on season
                    month = current_date.month
                    if 6 <= month <= 9:  # Monsoon season - higher chance of rain delay
                        if random.random() < 0.4:  # 40% chance of rain delay
                            delay_hours = random.uniform(4, 24)
                            delay_reason = "heavy rainfall (simulated)"
                            actual_time = scheduled_time + timedelta(hours=delay_hours)
                        else:
                            delay_hours = 0
                            delay_reason = None
                            actual_time = scheduled_time
                    else:  # Dry season - lower chance of rain delay
                        if random.random() < 0.1:  # 10% chance of rain delay
                            delay_hours = random.uniform(2, 8)
                            delay_reason = "moderate rainfall (simulated)"
                            actual_time = scheduled_time + timedelta(hours=delay_hours)
                        else:
                            delay_hours = 0
                            delay_reason = None
                            actual_time = scheduled_time
                    
                    # Other random delays
                    if delay_hours == 0 and random.random() < 0.1:  # 10% chance of other delay
                        delay_hours = random.uniform(1, 6)
                        delay_reason = random.choice([
                            "equipment malfunction", "safety inspection",
                            "personnel shortage", "regulatory delay"
                        ])
                        actual_time = scheduled_time + timedelta(hours=delay_hours)
                    
                    explosives_kg = random.uniform(500, 2000)  # 500-2000 kg of explosives
                    
                    blast = BlastRecord(
                        mine_id=mine.id,
                        scheduled_date=scheduled_time,
                        actual_date=actual_time if delay_hours > 0 else scheduled_time,
                        delay_hours=delay_hours if delay_hours > 0 else None,
                        delay_reason=delay_reason,
                        explosives_kg=explosives_kg,
                        source_tag=SourceTag.SYNTHETIC
                    )
                    db.add(blast)
                    records_added += 1
            
            current_date += timedelta(days=1)
        
        db.commit()
        print(f"Added {records_added} synthetic blast records")
        
    except Exception as e:
        db.rollback()
        print(f"Error generating synthetic blast data: {e}")
    finally:
        db.close()


def main():
    """Main function to generate synthetic blast data"""
    generate_synthetic_blast_data(years=2)


if __name__ == "__main__":
    main()
