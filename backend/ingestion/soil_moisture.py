"""
Soil moisture data ingestion using NASA SMAP via AppEEARS API
Data for MOIL mining belt: Nagpur/Bhandara (Maharashtra) and Chhindwara/Balaghat (Madhya Pradesh)
"""

import requests
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal
from models.schema import Mine, EnvObservation, SourceTag
import os
import time
import numpy as np


class AppEEARSIngestor:
    """Ingest soil moisture data from NASA SMAP via AppEEARS API"""
    
    def __init__(self, username: str = None, password: str = None):
        self.username = username or os.getenv('NASA_EARTHDATA_USERNAME')
        self.password = password or os.getenv('NASA_EARTHDATA_PASSWORD')
        self.base_url = "https://appeears.earthdatacloud.nasa.gov/api"
        self.token = None
        
        # Bounding box for MOIL mining belt
        self.bbox = [78.5, 21.0, 80.5, 22.5]  # [min_lon, min_lat, max_lon, max_lat]
    
    def login(self):
        """Authenticate with NASA Earthdata"""
        if not self.username or not self.password:
            print("Warning: NASA Earthdata credentials not provided")
            return False
        
        try:
            auth_url = f"{self.base_url}/user/login"
            response = requests.post(
                auth_url,
                auth=(self.username, self.password),
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            token_response = response.json()
            self.token = token_response.get('token')
            print("Successfully authenticated with NASA Earthdata")
            return True
            
        except Exception as e:
            print(f"Error authenticating with NASA Earthdata: {e}")
            return False
    
    def get_available_products(self):
        """Get list of available SMAP products from AppEEARS"""
        if not self.token:
            print("Not authenticated")
            return None
        
        try:
            url = f"{self.base_url}/product"
            response = requests.get(
                url,
                headers={'Authorization': f'Bearer {self.token}'}
            )
            response.raise_for_status()
            
            products = response.json()
            # Filter for SMAP soil moisture products
            smap_products = [p for p in products if 'SMAP' in p.get('Product', '')]
            print(f"Found {len(smap_products)} SMAP products")
            return smap_products
            
        except Exception as e:
            print(f"Error fetching products: {e}")
            return None
    
    def submit_task(self, start_date: str, end_date: str, product: str = "SPL3SMP_E.005"):
        """
        Submit a task to AppEEARS for SMAP soil moisture data
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            product: SMAP product ID
        """
        if not self.token:
            print("Not authenticated")
            return None
        
        try:
            task_url = f"{self.base_url}/task"
            
            task_json = {
                "taskType": "area",
                "taskName": f"SMAP_Soil_Moisture_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "params": {
                    "dates": [
                        {
                            "startDate": start_date,
                            "endDate": end_date
                        }
                    ],
                    "layers": [
                        {
                            "layer": "Soil_Moisture_Retrieval_Data_AM_soil_moisture",
                            "product": product
                        }
                    ],
                    "output": {
                        "format": {
                            "type": "geotiff"
                        },
                        "projection": "geographic"
                    },
                    "queue": "landstregt-1-0-0"
                },
                "bbox": self.bbox
            }
            
            response = requests.post(
                task_url,
                json=task_json,
                headers={'Authorization': f'Bearer {self.token}'}
            )
            response.raise_for_status()
            
            task = response.json()
            print(f"Submitted task: {task.get('task_id')}")
            return task.get('task_id')
            
        except Exception as e:
            print(f"Error submitting task: {e}")
            return None
    
    def check_task_status(self, task_id: str):
        """Check the status of a submitted task"""
        if not self.token:
            return None
        
        try:
            status_url = f"{self.base_url}/task/{task_id}"
            response = requests.get(
                status_url,
                headers={'Authorization': f'Bearer {self.token}'}
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error checking task status: {e}")
            return None
    
    def download_results(self, task_id: str):
        """Download results from a completed task"""
        status = self.check_task_status(task_id)
        if not status or status.get('status') != 'done':
            print(f"Task {task_id} not completed. Status: {status.get('status') if status else 'unknown'}")
            return None
        
        try:
            # Get bundle info
            bundle_url = f"{self.base_url}/bundle/{task_id}"
            response = requests.get(
                bundle_url,
                headers={'Authorization': f'Bearer {self.token}'}
            )
            response.raise_for_status()
            
            bundle = response.json()
            files = bundle.get('files', [])
            
            # Download files (simplified - in production would handle multiple files)
            print(f"Found {len(files)} files in bundle")
            return files
            
        except Exception as e:
            print(f"Error downloading results: {e}")
            return None
    
    def ingest_historical_data(self, years: int = 2):
        """
        Ingest historical SMAP soil moisture data
        
        Args:
            years: Number of years of historical data to ingest
        """
        if not self.login():
            print("Could not authenticate. Using synthetic data as fallback.")
            self.generate_synthetic_data(years)
            return
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365*years)
        
        print(f"Ingesting SMAP data from {start_date.date()} to {end_date.date()}")
        
        task_id = self.submit_task(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        if task_id:
            # Wait for task completion (simplified polling)
            print("Waiting for task completion...")
            for i in range(30):  # Poll for up to 30 minutes
                status = self.check_task_status(task_id)
                if status and status.get('status') == 'done':
                    print("Task completed successfully")
                    files = self.download_results(task_id)
                    # Process files into database (would need actual file processing)
                    print(f"Downloaded {len(files) if files else 0} files")
                    break
                elif status and status.get('status') == 'failed':
                    print("Task failed")
                    self.generate_synthetic_data(years)
                    break
                time.sleep(60)
            else:
                print("Task timed out")
                self.generate_synthetic_data(years)
        else:
            self.generate_synthetic_data(years)
    
    def generate_synthetic_data(self, years: int = 2):
        """Generate synthetic soil moisture data as fallback"""
        print("Generating synthetic soil moisture data as fallback")
        
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
                    # Generate synthetic soil moisture values (0-0.5 m³/m³)
                    # Higher in monsoon season (June-September)
                    month = current_date.month
                    if 6 <= month <= 9:  # Monsoon
                        base_moisture = 0.3 + np.random.uniform(-0.1, 0.1)
                    else:
                        base_moisture = 0.15 + np.random.uniform(-0.05, 0.05)
                    
                    moisture = max(0.05, min(0.5, base_moisture))
                    
                    obs = EnvObservation(
                        mine_id=mine.id,
                        observation_date=current_date.date(),
                        layer_type='soil_moisture',
                        value=moisture,
                        unit='m3/m3',
                        source_tag=SourceTag.SYNTHETIC
                    )
                    db.add(obs)
                    records_added += 1
                
                current_date += timedelta(days=1)
            
            db.commit()
            print(f"Added {records_added} synthetic soil moisture records")
            
        except Exception as e:
            db.rollback()
            print(f"Error generating synthetic data: {e}")
        finally:
            db.close()


def main():
    """Main function to run SMAP ingestion"""
    ingestor = AppEEARSIngestor()
    ingestor.ingest_historical_data(years=2)


if __name__ == "__main__":
    import numpy as np
    main()
