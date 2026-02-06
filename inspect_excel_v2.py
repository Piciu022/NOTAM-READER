import pandas as pd
import os

file_path = 'example.xlsx'

try:
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        exit(1)

    xl = pd.ExcelFile(file_path, engine='openpyxl')
    print(f"Sheets: {xl.sheet_names}")
    
    df = pd.read_excel(file_path, engine='openpyxl') # Reads first sheet
    print("\n--- Columns ---")
    print(df.columns.tolist())
    print("\n--- First 3 rows ---")
    print(df.head(3).to_string())
    
except Exception as e:
    print(f"An error occurred: {e}")
