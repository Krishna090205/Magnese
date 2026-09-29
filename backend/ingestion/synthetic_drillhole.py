"""
Synthetic drillhole and assay data generator
Generates structurally realistic drillhole data correlated with mine locations
"""

from sqlalchemy.orm import Session
from database import SessionLocal
from models.schema import Mine, Drillhole, AssayInterval, SourceTag
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from datetime import datetime, timedelta
import random
import numpy as np


def generate_synthetic_drillhole_data():
    """Generate synthetic drillhole and assay data"""
    print("Generating synthetic drillhole and assay data")
    
    db = SessionLocal()
    try:
        mines = db.query(Mine).all()
        if not mines:
            print("No mines found in database")
            return
        
        drillholes_added = 0
        assays_added = 0
        
        for mine in mines:
            # Generate 5-15 drillholes per mine
            num_drillholes = random.randint(5, 15)
            
            for i in range(num_drillholes):
                # Generate drillhole location near mine
                # Use approximate coordinates based on mine name
                if "Balaghat" in mine.name or "Ukwa" in mine.name or "Munsar" in mine.name:
                    mine_lon, mine_lat = 80.18, 21.80
                elif "Gumgaon" in mine.name or "Chikla" in mine.name:
                    mine_lon, mine_lat = 79.65, 21.17
                else:  # Nagpur area mines
                    mine_lon, mine_lat = 79.25, 21.20
                
                # Random offset within 5km
                offset_lon = random.uniform(-0.05, 0.05)
                offset_lat = random.uniform(-0.05, 0.05)
                
                drillhole_location = Point(mine_lon + offset_lon, mine_lat + offset_lat)
                
                # Generate drillhole data
                drill_date = datetime.now() - timedelta(days=random.randint(365, 3650))  # 1-10 years ago
                total_depth = random.uniform(50, 300)  # 50-300 meters
                
                drillhole = Drillhole(
                    mine_id=mine.id,
                    hole_id=f"{mine.name[:3].upper()}-DH-{i+1:03d}",
                    location=from_shape(drillhole_location, srid=4326),
                    total_depth_m=total_depth,
                    drill_date=drill_date.date(),
                    source_tag=SourceTag.SYNTHETIC
                )
                db.add(drillhole)
                db.flush()  # Flush to get the drillhole ID
                drillholes_added += 1
                
                # Generate assay intervals (every 5-10 meters)
                current_depth = 0
                while current_depth < total_depth:
                    interval_length = random.uniform(5, 10)
                    to_depth = min(current_depth + interval_length, total_depth)
                    
                    # Generate assay values correlated with depth
                    # Deeper intervals tend to have higher Mn content
                    depth_factor = current_depth / total_depth
                    base_mn = 25 + (depth_factor * 20) + random.uniform(-5, 5)  # 20-50% Mn
                    mn_percent = max(5, min(55, base_mn))
                    
                    fe_percent = random.uniform(5, 15)  # 5-15% Fe
                    sio2_percent = random.uniform(20, 40)  # 20-40% SiO2
                    al2o3_percent = random.uniform(5, 15)  # 5-15% Al2O3
                    
                    assay = AssayInterval(
                        drillhole_id=drillhole.id,
                        from_depth_m=current_depth,
                        to_depth_m=to_depth,
                        mn_percent=mn_percent,
                        fe_percent=fe_percent,
                        sio2_percent=sio2_percent,
                        al2o3_percent=al2o3_percent,
                        source_tag=SourceTag.SYNTHETIC
                    )
                    db.add(assay)
                    assays_added += 1
                    
                    current_depth = to_depth
        
        db.commit()
        print(f"Added {drillholes_added} synthetic drillholes and {assays_added} assay intervals")
        
    except Exception as e:
        db.rollback()
        print(f"Error generating synthetic drillhole data: {e}")
    finally:
        db.close()


def main():
    """Main function to generate synthetic drillhole data"""
    generate_synthetic_drillhole_data()


if __name__ == "__main__":
    main()
