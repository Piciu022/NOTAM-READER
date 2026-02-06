# NOTAM Reader

## Project Overview
NOTAM Reader is a tool designed to analyze Notices to Airmen (NOTAMs) relevant to specific flight operations. 
The goal is to automatically filter and present NOTAMs that affect a specific flight path (Origin -> Destination) within a specific timeframe.

## Current Architecture

### Core Modules
- **`app.py`**: Main Flask web application serving the interface.
- **`database.py`**: Manages the SQLite connection (`notams.db`).
- **`decoder.py`**: (Presumably) Handles parsing/decoding of raw NOTAM text.
- **`flight_schedule.py`**: **[NEW]** Handles reading and parsing of flight schedules from Excel files (e.g., `example.xlsx`).

### Data
- **`notams.db`**: SQLite database storing NOTAMs.
- **`example.xlsx`**: Sample flight schedule file.

## Recent Changes (Flight Schedule Integration)
We have implemented a `FlightScheduleReader` in `flight_schedule.py` that processes the Excel schedule.
- **Input**: Excel file with columns `Orig`, `Dest`, `Al` (Airline), `FltNbr`, `Date-LT`, `Std-LT`, `Sta-LT`.
- **Output**: List of `Flight` objects containing parsed datetimes and airport codes.
- **Testing**: Run `python3 test_flight_schedule.py` to verify the reader works against `example.xlsx`.

## Usage
1. **Setup**: Ensure you have a virtual environment.
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt  # (Ensure pandas, openpyxl, flask are installed)
   ```
2. **Run Flight Reader Test**:
   ```bash
   python3 test_flight_schedule.py
   ```
3. **Run Web App**:
   ```bash
   python3 app.py
   ```

## Roadmap / Next Steps for Contributors

### 1. Integration (Immediate Priority)
The next major step is to connect the parsed flights with the NOTAM database.
- **Objective**: For a given `Flight` object, find all matching NOTAMs.
- **Logic Needed**:
    - **Time Filter**: `NOTAM_Start <= Flight_Arrival + Buffer` AND `NOTAM_End >= Flight_Departure - Buffer`.
    - **Location Filter**: Match NOTAM Q-code locations or A/B fields with Flight Origin/Destination (and potentially alternate airports).

### 2. Decoder Enhancement
- Ensure `decoder.py` correctly extracts start/end validity times and coordinate/radius information from NOTAMs to support the filtering logic above.

### 3. User Interface
- Create a page to upload/select a Flight Schedule Excel file.
- Display a list of parsed flights.
- Clicking a flight should trigger the NOTAM check and display results.

### 4. Optimization
- The current Excel reader loads the full file if `usecols` fails. Ensure column mapping remains robust if the Excel format changes.
