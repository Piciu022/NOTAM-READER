import pandas as pd
import os

file_path = 'example.xlsx'

try:
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        exit(1)

    # Read the excel file
    df = pd.read_excel(file_path, engine='openpyxl')
    
    print("--- Columns ---")
    print(df.columns.tolist())
    print("\n--- First 5 rows ---")
    print(df.head().to_string())
    print("\n--- Cartesian products of airport codes check (first row) ---")
    # User mentioned: "na początku 3 litery lotniska z kodów IATA , następnie slesz, znowu trzy litery kodu lotniska gdzie ląduje rejs"
    # Let's see if we can identify this column.
    
except Exception as e:
    print(f"An error occurred: {e}")
