import csv
import psycopg2
from dotenv import load_dotenv
import os
from fmp_client import FMPAPIClient

load_dotenv()
API_KEY = os.getenv("API_KEY")

# PostgreSQL configuration
DB_CONFIG = {
    "host": "localhost",
    "database": "chain8_fmp",
    "user": "chain8_fmp",
    "password": "chain8_fmp",
    "port": "5433"
}

client = FMPAPIClient(API_KEY)

# Fetch Indian Companies List
def fetch_indian_companies_list():
    """Fetch a list of all Indian companies."""
    stock_list = client.fetch_stock_list()
    if not stock_list:
        print("No stock data fetched.")
        return []

    indian_exchanges = ["NSE", "BSE"]
    indian_companies = [
        stock for stock in stock_list if stock.get("exchangeShortName") in indian_exchanges
    ]
    print(f"Total Indian Companies Found: {len(indian_companies)}")
    return indian_companies

def save_to_csv(data, filename):
    """Save data to a CSV file."""
    if not data:
        print("No data to save.")
        return

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"Data saved to {filename}")
    
def push_to_postgres(data):
    """Push Indian companies list to PostgreSQL."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS indian_companies_list (
            symbol TEXT PRIMARY KEY,
            name TEXT,
            exchange TEXT,
            exchangeShortName TEXT,
            price FLOAT,
            type TEXT
        );
        """
        cur.execute(create_table_query)

        for company in data:
            insert_query = """
            INSERT INTO indian_companies_list (symbol, name, exchange, exchangeShortName, price, type)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol) DO NOTHING;
            """
            cur.execute(insert_query, (
                company.get("symbol"),
                company.get("name"),
                company.get("exchange"),
                company.get("exchangeShortName"),
                company.get("price"),
                company.get("type")
            ))

        conn.commit()
        cur.close()
        conn.close()
        print("Indian Companies List successfully pushed to PostgreSQL.")
    except Exception as e:
        print(f"Error pushing Indian Companies List to PostgreSQL: {e}")

if __name__ == "__main__":
    indian_companies = fetch_indian_companies_list()
    # save_to_csv(indian_companies, "indian_companies_list.csv")
    push_to_postgres(indian_companies)


