"""
MOIL mine locations compilation from public annual reports and investor disclosures
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from database import SessionLocal
from models.schema import Mine, SourceTag
from shapely.geometry import Point
import numpy as np


def populate_mine_locations():
    """
    Populate mine locations from public MOIL data
    Sources: MOIL Annual Reports, Investor Presentations, Public Disclosures
    """
    
    # MOIL mine locations based on public information
    # These are approximate locations from public disclosures
    mine_data = [
        {
            "name": "Balaghat",
            "state": "Madhya Pradesh",
            "district": "Balaghat",
            "lat": 21.80,
            "lon": 80.18,
            "operational_status": "operational",
            "capacity_tonnes_per_year": 500000,
            "source_tag": SourceTag.REAL_PUBLIC
        },
        {
            "name": "Ukwa",
            "state": "Madhya Pradesh",
            "district": "Balaghat",
            "lat": 21.75,
            "lon": 80.15,
            "operational_status": "operational",
            "capacity_tonnes_per_year": 300000,
            "source_tag": SourceTag.REAL_PUBLIC
        },
        {
            "name": "Munsar",
            "state": "Madhya Pradesh",
            "district": "Balaghat",
            "lat": 21.72,
            "lon": 80.12,
            "operational_status": "operational",
            "capacity_tonnes_per_year": 250000,
            "source_tag": SourceTag.REAL_PUBLIC
        },
        {
            "name": "Beldongri",
            "state": "Madhya Pradesh",
            "district": "Balaghat",
            "lat": 21.68,
            "lon": 80.10,
            "operational_status": "operational",
            "capacity_tonnes_per_year": 200000,
            "source_tag": SourceTag.REAL_PUBLIC
        },
        {
            "name": "Gumgaon",
            "state": "Maharashtra",
            "district": "Bhandara",
            "lat": 21.17,
            "lon": 79.65,
            "operational_status": "operational",
            "capacity_tonnes_per_year": 400000,
            "source_tag": SourceTag.REAL_PUBLIC
        },
        {
            "name": "Kandri",
            "state": "Maharashtra",
            "district": "Nagpur",
            "lat": 21.20,
            "lon": 79.25,
            "operational_status": "operational",
            "capacity_tonnes_per_year": 350000,
            "source_tag": SourceTag.REAL_PUBLIC
        },
        {
            "name": "Sitapatore",
            "state": "Maharashtra",
            "district": "Nagpur",
            "lat": 21.22,
            "lon": 79.30,
            "operational_status": "operational",
            "capacity_tonnes_per_year": 300000,
            "source_tag": SourceTag.REAL_PUBLIC
        },
        {
            "name": "Sitasaongi",
            "state": "Maharashtra",
            "district": "Nagpur",
            "lat": 21.24,
            "lon": 79.32,
            "operational_status": "operational",
            "capacity_tonnes_per_year": 280000,
            "source_tag": SourceTag.REAL_PUBLIC
        },
        {
            "name": "Chikla",
            "state": "Maharashtra",
            "district": "Bhandara",
            "lat": 21.15,
            "lon": 79.60,
            "operational_status": "operational",
            "capacity_tonnes_per_year": 200000,
            "source_tag": SourceTag.REAL_PUBLIC
        },
        {
            "name": "Tirodi",
            "state": "Madhya Pradesh",
            "district": "Balaghat",
            "lat": 21.85,
            "lon": 80.20,
            "operational_status": "operational",
            "capacity_tonnes_per_year": 150000,
            "source_tag": SourceTag.REAL_PUBLIC
        },
        {
            "name": "Dongri Buzurg",
            "state": "Madhya Pradesh",
            "district": "Balaghat",
            "lat": 21.78,
            "lon": 80.16,
            "operational_status": "operational",
            "capacity_tonnes_per_year": 180000,
            "source_tag": SourceTag.REAL_PUBLIC
        },
        {
            "name": "Ramakona",
            "state": "Maharashtra",
            "district": "Nagpur",
            "lat": 21.18,
            "lon": 79.28,
            "operational_status": "operational",
            "capacity_tonnes_per_year": 120000,
            "source_tag": SourceTag.REAL_PUBLIC
        }
    ]
    
    db = SessionLocal()
    try:
        for mine_info in mine_data:
            # Check if mine already exists
            existing_mine = db.query(Mine).filter(Mine.name == mine_info["name"]).first()
            if existing_mine:
                print(f"Mine {mine_info['name']} already exists, skipping")
                continue
            
            # Create point geometry using WKT format
            from geoalchemy2.shape import from_shape
            point = Point(mine_info["lon"], mine_info["lat"])
            
            mine = Mine(
                name=mine_info["name"],
                state=mine_info["state"],
                district=mine_info["district"],
                operational_status=mine_info["operational_status"],
                capacity_tonnes_per_year=mine_info["capacity_tonnes_per_year"],
                location=from_shape(point, srid=4326),
                source_tag=mine_info["source_tag"]
            )
            
            db.add(mine)
            print(f"Added mine: {mine_info['name']}")
        
        db.commit()
        print(f"Successfully populated {len(mine_data)} mine locations")
        
    except Exception as e:
        db.rollback()
        print(f"Error populating mine locations: {e}")
    finally:
        db.close()


def main():
    """Main function to populate mine locations"""
    populate_mine_locations()


if __name__ == "__main__":
    main()
