from pathlib import Path
import pandas as pd

RAW_DATA_PATH = Path("data/raw")

csv_files = list(RAW_DATA_PATH.glob("*.csv"))

if not csv_files:
    print("No CSV files found in data/raw")
    exit()

print(f"Found {len(csv_files)} CSV files\n")

for file in sorted(csv_files):
    try:
        df = pd.read_csv(file)

        print("=" * 70)
        print(f"File: {file.name}")
        print(f"Rows: {len(df)}")
        print(f"Columns: {len(df.columns)}")
        print(f"Column names: {list(df.columns)}")
        print("\nMissing values:")
        print(df.isnull().sum())
        print("\nSample records:")
        print(df.head(3).to_string(index=False))

    except Exception as error:
        print(f"Error reading {file.name}: {error}")

print("\nDataset inspection completed.")