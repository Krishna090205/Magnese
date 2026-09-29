"""
Synthetic equipment event data generator
Generates structurally realistic equipment downtime events
"""

from sqlalchemy.orm import Session
from database import SessionLocal
from models.schema import Mine, EquipmentEvent, SourceTag
from datetime import datetime, timedelta
import random


def generate_synthetic_equipment_data(years: int = 2):
    """Generate synthetic equipment event data"""
    print(f"Generating synthetic equipment event data for {years} years")
    
    db = SessionLocal()
    try:
        mines = db.query(Mine).all()
        if not mines:
            print("No mines found in database")
            return
        
        # Common equipment types in mining
        equipment_types = [
            "EXCAVATOR-01", "EXCAVATOR-02", "DRILL-RIG-01", "DRILL-RIG-02",
            "DUMPER-01", "DUMPER-02", "DUMPER-03", "CRUSHER-01",
            "CONVEYOR-01", "LOADER-01", "GRADER-01"
        ]
        
        event_types = ["breakdown", "maintenance", "inspection", "upgrade"]
        causes = [
            "hydraulic failure", "engine overheating", "electrical fault",
            "wear and tear", "scheduled maintenance", "inspection",
            "software upgrade", "safety inspection"
        ]
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365*years)
        
        events_added = 0
        current_date = start_date
        
        while current_date <= end_date:
            for mine in mines:
                # Random chance of equipment event each day (5-15%)
                if random.random() < 0.10:
                    equipment_id = random.choice(equipment_types)
                    event_type = random.choice(event_types)
                    cause = random.choice(causes)
                    
                    start_time = current_date + timedelta(hours=random.randint(8, 16))
                    
                    # Duration depends on event type
                    if event_type == "breakdown":
                        duration_hours = random.uniform(4, 48)
                    elif event_type == "maintenance":
                        duration_hours = random.uniform(2, 12)
                    else:  # inspection/upgrade
                        duration_hours = random.uniform(1, 8)
                    
                    end_time = start_time + timedelta(hours=duration_hours)
                    
                    event = EquipmentEvent(
                        mine_id=mine.id,
                        equipment_id=equipment_id,
                        event_type=event_type,
                        start_time=start_time,
                        end_time=end_time,
                        downtime_hours=duration_hours,
                        cause=cause,
                        source_tag=SourceTag.SYNTHETIC
                    )
                    db.add(event)
                    events_added += 1
            
            current_date += timedelta(days=1)
        
        db.commit()
        print(f"Added {events_added} synthetic equipment events")
        
    except Exception as e:
        db.rollback()
        print(f"Error generating synthetic equipment data: {e}")
    finally:
        db.close()


def main():
    """Main function to generate synthetic equipment data"""
    generate_synthetic_equipment_data(years=2)


if __name__ == "__main__":
    main()
