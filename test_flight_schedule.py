from flight_schedule import FlightScheduleReader
import os

def test_reader():
    file_path = 'example.xlsx'
    if not os.path.exists(file_path):
        print(f"Skipping test: {file_path} not found.")
        return

    reader = FlightScheduleReader()
    flights = reader.read_file(file_path)
    
    print(f"Successfully read {len(flights)} flights.")
    
    if len(flights) > 0:
        f = flights[0]
        print(f"First Flight: {f}")
        
        # Verify specific values from inspection
        # 1  WAW / ORD ... LO 1 ... 11APR26 12:00:00
        assert f.origin == "WAW"
        assert f.destination == "ORD"
        assert f.airline_code == "LO"
        assert f.flight_number == "1"
        assert f.departure_time.year == 2026
        assert f.departure_time.month == 4
        assert f.departure_time.day == 11
        assert f.departure_time.hour == 12
        assert f.departure_time.minute == 0
        
        print("Verification passed for first row.")

if __name__ == "__main__":
    test_reader()
