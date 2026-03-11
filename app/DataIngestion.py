# data_ingestion.py
# @ingest_data

import pandas as pd
import os
import logging

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def ingest_data(file_path):
    # Check if file exists
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return None

    try:
        # Read data from the CSV file
        data = pd.read_csv(file_path)

        # Log the success and number of records loaded
        logging.info(f"Successfully loaded {len(data)} records from {file_path}")

        # Optionally, check for expected columns (if needed)
        required_columns = ['temperature', 'humidity', 'co2_levels']  # Example columns
        if not all(col in data.columns for col in required_columns):
            logging.warning(
                f"Some expected columns are missing: "
                f"{set(required_columns) - set(data.columns)}"
            )

        return data

    except Exception as e:
        # Log any error that occurs
        logging.error(f"Error loading data from {file_path}: {e}")
        return None

# Example usage:
if __name__ == "__main__":
    file_path = "data/climate_data.csv"  # Adjust the path if necessary
    data = ingest_data(file_path)

    if data is not None:
        # Process the data further if needed
        print(data.head())  # Example of printing the first few rows
