from pathlib import Path
from datetime import datetime
import pandas as pd

# Project paths
SOURCE_PATH = Path("data/raw")
DATA_LAKE_PATH = Path("data/lake/raw")

# Create the destination directory
DATA_LAKE_PATH.mkdir(parents=True, exist_ok=True)


def ingest_csv_to_parquet(csv_file: Path):
    """Read a CSV file and store it as a Parquet file."""

    print(f"\nReading: {csv_file.name}")

    start_time = datetime.now()

    # Read the source CSV
    dataframe = pd.read_csv(csv_file, low_memory=False)

    # Create the destination filename
    parquet_file = DATA_LAKE_PATH / f"{csv_file.stem}.parquet"

    # Save as Parquet
    dataframe.to_parquet(
        parquet_file,
        index=False
    )

    elapsed_time = datetime.now() - start_time

    print(f"Rows processed: {len(dataframe):,}")
    print(f"Saved to: {parquet_file}")
    print(f"Time taken: {elapsed_time}")


def main():
    csv_files = sorted(SOURCE_PATH.glob("*.csv"))

    if not csv_files:
        print("No CSV files found in data/raw")
        return

    print(f"Found {len(csv_files)} CSV files")
    print("Starting ingestion...\n")

    for csv_file in csv_files:
        try:
            ingest_csv_to_parquet(csv_file)
        except Exception as error:
            print(f"Error processing {csv_file.name}: {error}")

    print("\nIngestion completed successfully!")


if __name__ == "__main__":
    main()