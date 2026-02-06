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
        Adjusted for actual columns: Routing, Al, FltNbr, Date-LT, Std-LT, Sta-LT, Orig, Dest, etc.
        """
        
        # Columns mapped to internal needs
        # Orig -> origin
        # Dest -> destination
        # Al -> airline_code
        # FltNbr -> flight_number
        # Date-LT -> date part of departure
        # Std-LT -> time part of departure
        # Sta-LT -> time part of arrival
        # Diff-LT -> days offset for arrival (optional, assumed 0 if NaN)

        required_cols = ['Orig', 'Dest', 'Al', 'FltNbr', 'Date-LT', 'Std-LT', 'Sta-LT']
        
        try:
            # Load specific columns
            # Note: 'Diff-LT' might be useful so include it if present, but don't fail if missing?
            # Let's read broadly to be safe, filtering later
            df = pd.read_excel(file_path, engine='openpyxl')
        except Exception as e:
            print(f"Error reading excel: {e}")
            return []

        # Clean column names
        df.columns = df.columns.astype(str).str.strip()
        
        # Verify required columns
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
             # Fallback: maybe 'Itinerary' exists? No, we saw the cols.
             print(f"Error: Missing required columns: {missing}")
             print(f"Available: {df.columns.tolist()}")
             return []

        flights = []
        
        for index, row in df.iterrows():
            try:
                # Basic fields
                origin = str(row['Orig']).strip()
                destination = str(row['Dest']).strip()
                airline = str(row['Al']).strip()
                flt_no = str(row['FltNbr']).strip()
                
                # Times
                date_lt_raw = row['Date-LT'] # Expected 04APR26
                std_lt_raw = row['Std-LT']   # Expected 12:00:00
                sta_lt_raw = row['Sta-LT']   # Expected 15:10:00
                
                # Calculate Departure Datetime
                departure_dt = self._combine_date_time(date_lt_raw, std_lt_raw)
                
                # Calculate Arrival Datetime
                # Base arrival date is same as departure date
                arrival_dt_base = self._combine_date_time(date_lt_raw, sta_lt_raw)
                
                # Handle day crossing (arrival time < departure time usually means +1 day, 
                # but explicit Diff-LT is better if available)
                day_offset = 0
                if 'Diff-LT' in row and pd.notna(row['Diff-LT']):
                     try:
                         day_offset = int(row['Diff-LT'])
                     except:
                         pass
                elif arrival_dt_base < departure_dt:
                     # Heuristic: if arrival is before departure, add 1 day
                     # (Assumes flight < 24h and no negative time travel > 24h, reasonable for commercial)
                     day_offset = 1
                
                arrival_dt = arrival_dt_base + timedelta(days=day_offset)

                flights.append(Flight(
                    origin=origin,
                    destination=destination,
                    airline_code=airline,
                    flight_number=flt_no,
                    departure_time=departure_dt,
                    arrival_time=arrival_dt
                ))
            except Exception as e:
                # Print error for debugging
                if index < 5: 
                    print(f"Error on row {index}: {e}")
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

