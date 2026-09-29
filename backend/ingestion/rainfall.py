"""
Rainfall data ingestion using CHIRPS (Climate Hazards Group InfraRed Precipitation with Stations)
Data for MOIL mining belt: Nagpur/Bhandara (Maharashtra) and Chhindwara/Balaghat (Madhya Pradesh)
"""

import requests
import xarray as xr
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal
from models.schema import Mine, EnvObservation, SourceTag
import numpy as np


class CHIRPSIngestor:
    """Ingest rainfall data from CHIRPS via IRI Data Library"""
    
    def __init__(self):
        # Approximate bounding box for MOIL mining belt
        # Maharashtra: Nagpur (21.15°N, 79.09°E), Bhandara (21.17°N, 79.65°E)
        # Madhya Pradesh: Chhindwara (22.07°N, 78.93°E), Balaghat (21.80°N, 80.18°E)
        self.bbox = {
            'min_lat': 21.0,
            'max_lat': 22.5,
            'min_lon': 78.5,
            'max_lon': 80.5
        }
        self.base_url = "https://iridl.ldeo.columbia.edu/SOURCES/.UCSB/.CHG/.CHIRPS/.daily/.precipitation"
    
    def fetch_data(self, start_date: str, end_date: str) -> xr.Dataset:
        """
        Fetch CHIRPS daily precipitation data for the specified date range and bounding box
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            xarray Dataset with precipitation data
        """
        try:
            # Construct the IRI Data Library URL
            url = f"{self.base_url}/.X/{self.bbox['min_lon']}/{self.bbox['max_lon']}/.Y/{self.bbox['min_lat']}/{self.bbox['max_lat']}"
            url += f"/.T/{start_date.replace('-', '')}/{end_date.replace('-', '')}/.nc"
            
            print(f"Fetching CHIRPS data from {url}")
            response = requests.get(url, timeout=300)
            response.raise_for_status()
            
            # Save to temporary file and load with xarray
            temp_file = "/tmp/chirps_temp.nc"
            with open(temp_file, 'wb') as f:
                f.write(response.content)
            
            ds = xr.open_dataset(temp_file)
            return ds
            
        except Exception as e:
            print(f"Error fetching CHIRPS data: {e}")
            return None
    
    def process_to_database(self, ds: xr.Dataset, mine_id: int = None):
        """
        Process CHIRPS data and insert into database
        
        Args:
            ds: xarray Dataset with CHIRPS data
            mine_id: Optional mine ID to associate data with
        """
        if ds is None:
            print("No data to process")
            return
        
        db = SessionLocal()
        try:
            # Get mines if mine_id not specified
            if mine_id is None:
                mines = db.query(Mine).all()
            else:
                mines = [db.query(Mine).filter(Mine.id == mine_id).first()]
            
            if not mines:
                print("No mines found in database")
                return
            
            # Convert to pandas for easier processing
            df = ds.to_dataframe().reset_index()
            
            # Process each day
            records_added = 0
            for _, row in df.iterrows():
                if 'precipitation' in row and not np.isnan(row['precipitation']):
                    # For each mine, find nearest grid point
                    for mine in mines:
                        if mine.location:
                            # Simple nearest neighbor (could be improved with proper spatial indexing)
                            obs = EnvObservation(
                                mine_id=mine.id,
                                observation_date=row['T'],
                                layer_type='rainfall',
                                value=float(row['precipitation']),
                                unit='mm/day',
                                source_tag=SourceTag.REAL_PUBLIC
                            )
                            db.add(obs)
                            records_added += 1
            
            db.commit()
            print(f"Added {records_added} rainfall records to database")
            
        except Exception as e:
            db.rollback()
            print(f"Error processing data to database: {e}")
        finally:
            db.close()
    
    def ingest_historical_data(self, years: int = 2):
        """
        Ingest historical CHIRPS data for the specified number of years
        
        Args:
            years: Number of years of historical data to ingest
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365*years)
        
        print(f"Ingesting CHIRPS data from {start_date.date()} to {end_date.date()}")
        
        ds = self.fetch_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        if ds:
            self.process_to_database(ds)


def main():
    """Main function to run CHIRPS ingestion"""
    ingestor = CHIRPSIngestor()
    ingestor.ingest_historical_data(years=2)


if __name__ == "__main__":
    main()
