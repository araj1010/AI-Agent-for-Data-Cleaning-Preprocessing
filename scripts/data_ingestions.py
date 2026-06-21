import os
import pandas as pd
import requests
from sqlalchemy import create_engine

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")

class DataIngestion:
    def __init__(self, db_url=None):
        """Initialize the DataIngestion class with an optional database URL."""
        self.engine = create_engine(db_url) if db_url else None
    
    def load_csv(self, file_name):  
        """Load a CSV file into a pandas DataFrame."""
        file_path = os.path.join(DATA_DIR, file_name)
        try:
            df = pd.read_csv(file_path)
            print(f"✅ Loaded CSV file: {file_path}")
            return df
        except Exception as e:
            print(f"❌ Error loading CSV file: {e}")
            return None
        
    def load_excel(self, file_name, sheet_name=0): 
        """Load an Excel file into a pandas DataFrame."""
        file_path = os.path.join(DATA_DIR, file_name)
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"✅ Loaded Excel file: {file_path}")
            return df
        except Exception as e:
            print(f"❌ Error loading Excel file: {e}")
            return None

    def connect_database(self,db_url):
        """Establish a connection to the database using SQLAlchemy."""
        try:
            self.engine = create_engine(db_url)
            print("✅ Connected to the database successfully")
        except Exception as e:
            print(f"❌ Error connecting to the database: {e}")

    def load_from_database(self, query):  
        """Load data from the database using a SQL query."""
        if not self.engine:
            print("❌ Database connection not established.")
            return None
        from sqlalchemy import text
        try:
            with self.engine.connect() as conn:
                df = pd.read_sql(text(query), conn)
            print("✅ Loaded data from the database successfully")
            return df
        except Exception as e:
            print(f"❌ Error loading data from the database: {e}")
            return None

    
    def fetch_from_api(self, api_url, params=None):  
        """Fetch data from an API and return it as a pandas DataFrame."""
        try:
            response = requests.get(api_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    if 'data' in data and isinstance(data['data'], list):
                        data = data['data']
                    else:
                        data = [data]
                df = pd.json_normalize(data, sep='.')
                print(f"✅ Fetched data from API: {api_url}")
                return df
            else:
                print(f"❌ API request failed with status code: {response.status_code}")
                return None
            
        except Exception as e:
            print(f"❌ Error fetching data from API: {e}")
            return None