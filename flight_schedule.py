from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional
import pandas as pd

@dataclass
class Flight:
    origin: str
    destination: str
    airline_code: str  # e.g., "LO"
    flight_number: str # e.g., "1"
    departure_time: datetime
    arrival_time: datetime
    
    @property
    def flight_designator(self) -> str:
        return f"{self.airline_code} {self.flight_number}"

class FlightScheduleReader:
    def __init__(self):
        pass

    def parse_date(self, date_str: str) -> datetime:
        """Parses date string specifically for format like '11APR26' (DDMMMYY)."""
        # Try-except block for robustness, though we expect clean data in this column based on example
        try:
            return datetime.strptime(date_str, "%d%b%y")
        except ValueError as e:
            raise ValueError(f"Could not parse date: {date_str}. Expected format DDMMMYY (e.g., 11APR26)") from e

    def read_file(self, file_path: str) -> List[Flight]:
        """
        Reads the flight schedule from an Excel file.
        """
        required_cols = ['Itinerary', 'Designator', 'Flt No', 'Dep Date', 'Dep Time', 'Arr Date', 'Arr Time']
        
        try:
            # Try efficient load first
            df = pd.read_excel(file_path, usecols=required_cols, engine='openpyxl')
        except ValueError as e:
            print(f"Warning: usecols failed ({e}), loading full file.")
            df = pd.read_excel(file_path, engine='openpyxl')

        # Clean column names
        df.columns = df.columns.astype(str).str.strip()
        
        print(f"Debug: Loaded columns: {df.columns.tolist()}")

        # Verify required columns exist
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            print(f"Error: Missing required columns: {missing}")
            return []

        flights = []
        
        for index, row in df.iterrows():
            try:
                # Parse Itinerary
                itinerary = str(row['Itinerary'])
                if '/' not in itinerary:
                    continue # Skip invalid rows
                
                parts = itinerary.split('/')
                if len(parts) < 2:
                    continue
                
                origin = parts[0].strip()
                destination = parts[1].strip()
                
                # Parse Flight Info
                airline = str(row['Designator']).strip()
                flt_no = str(row['Flt No']).strip()
                
                dep_date_raw = row['Dep Date']
                dep_time_raw = row['Dep Time']
                arr_date_raw = row['Arr Date']
                arr_time_raw = row['Arr Time']

                departure_dt = self._combine_date_time(dep_date_raw, dep_time_raw)
                arrival_dt = self._combine_date_time(arr_date_raw, arr_time_raw)
                
                flights.append(Flight(
                    origin=origin,
                    destination=destination,
                    airline_code=airline,
                    flight_number=flt_no,
                    departure_time=departure_dt,
                    arrival_time=arrival_dt
                ))
            except Exception as e:
                # Print full error for first few failures
                print(f"Error on row {index}: {type(e).__name__}: {e}")
                continue
                
        return flights

    def _combine_date_time(self, date_val, time_val) -> datetime:
        """Helper to combine date and time components into a datetime object."""
        # Handle Date
        if isinstance(date_val, datetime):
            d = date_val.date()
        elif isinstance(date_val, str):
            d = self.parse_date(date_val).date()
        else:
            # Maybe pandas Timestamp
            if hasattr(date_val, 'date'):
                d = date_val.date()
            else:
                 raise ValueError(f"Unknown date format: {type(date_val)} {date_val}")

        # Handle Time
        t = None
        if isinstance(time_val, str):
            # Parse '12:00:00'
            try:
                t = datetime.strptime(time_val, "%H:%M:%S").time()
            except:
                # Try without seconds?
                t = datetime.strptime(time_val, "%H:%M").time()
        elif hasattr(time_val, 'hour'): # datetime.time or datetime or Timestamp
             t = time_val
        else:
             raise ValueError(f"Unknown time format: {type(time_val)} {time_val}")
             
        return datetime.combine(d, t)

