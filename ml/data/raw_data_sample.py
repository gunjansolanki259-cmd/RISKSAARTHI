import pandas as pd
import mysql.connector
import os
from app.config import settings


# ------------------------------------------------
# DB Connection
# ------------------------------------------------
def get_connection():
    return mysql.connector.connect(
        host=settings.DB_HOST,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME
    )


# ------------------------------------------------
# Resolve dynamic project path
# ------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Ensure directory exists
os.makedirs(DATA_DIR, exist_ok=True)

FILE_PATH = os.path.join(DATA_DIR, "raw_data_sample.csv")


# ------------------------------------------------
# Fetch Data
# ------------------------------------------------
def fetch_sample_data(limit=500000):
    conn = get_connection()

    try:
        query = f"SELECT * FROM loan_data ORDER BY RAND() LIMIT {limit}"
        df = pd.read_sql(query, conn)

        # Save CSV (dynamic path)
        df.to_csv(FILE_PATH, index=False)

        print(f"Data saved at: {FILE_PATH}")
        print("\nDefault Distribution:")
        print(df['default'].value_counts(normalize=True))

    finally:
        conn.close()


# ------------------------------------------------
# Run Script
# ------------------------------------------------
if __name__ == "__main__":
    fetch_sample_data()