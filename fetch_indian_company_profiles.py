import csv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
import os
import psycopg2
from fmp_client import FMPAPIClient  # Assuming fmp_client.py contains FMPAPIClient class

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")

# Initialize FMP API Client
client = FMPAPIClient(API_KEY)

# PostgreSQL configuration
DB_CONFIG = {
    "host": "localhost",
    "database": "chain8_fmp",
    "user": "chain8_fmp",
    "password": "chain8_fmp",
    "port": "5433"
}
def fetch_profile(symbol):
    """Fetch the profile of a single company."""
    try:
        profile = client.fetch_company_profile(symbol)
        if profile:
            return profile[0]  # Return the first object in the response
    except Exception as e:
        print(f"Error fetching profile for {symbol}: {e}")
    return None

def fetch_company_profiles(symbols, max_workers=3):
    """
    Fetch company profiles using multithreading.
    Limits to 3 requests per second to comply with API rate limits.
    """
    total_profiles = []
    failed_requests = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_profile, symbol): symbol for symbol in symbols}

        start_time = time.time()
        for future in as_completed(futures):
            symbol = futures[future]
            try:
                profile = future.result()
                if profile:
                    total_profiles.append(profile)
                else:
                    failed_requests.append(symbol)
            except Exception as e:
                print(f"Error processing {symbol}: {e}")
                failed_requests.append(symbol)

            # Ensure rate limiting (3 requests per second)
            if len(total_profiles) % max_workers == 0:
                elapsed = time.time() - start_time
                if elapsed < 1:  # Enforce 1-second delay if less than 1 second has passed
                    time.sleep(1 - elapsed)
                start_time = time.time()

    print(f"Total profiles fetched: {len(total_profiles)}")
    print(f"Failed requests: {len(failed_requests)}")

    # Retry failed requests
    if failed_requests:
        print("Retrying failed requests...")
        retry_profiles = fetch_company_profiles(failed_requests, max_workers=max_workers)
        total_profiles.extend(retry_profiles)

    return total_profiles

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
    """Push company profiles to PostgreSQL."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS indian_company_profiles (
            symbol TEXT PRIMARY KEY,
            price FLOAT,
            beta FLOAT,
            volAvg INTEGER,
            mktCap BIGINT,
            lastDiv FLOAT,
            range TEXT,
            changes FLOAT,
            companyName TEXT,
            currency TEXT,
            cik TEXT,
            isin TEXT,
            cusip TEXT,
            exchange TEXT,
            exchangeShortName TEXT,
            industry TEXT,
            website TEXT,
            description TEXT,
            ceo TEXT,
            sector TEXT,
            country TEXT,
            fullTimeEmployees TEXT,
            phone TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            zip TEXT,
            dcfDiff FLOAT,
            dcf FLOAT,
            ipoDate DATE
        );
        """
        cur.execute(create_table_query)

        # Define the columns to match the table schema
        columns = [
            "symbol", "price", "beta", "volAvg", "mktCap", "lastDiv", "range", "changes",
            "companyName", "currency", "cik", "isin", "cusip", "exchange", "exchangeShortName",
            "industry", "website", "description", "ceo", "sector", "country", "fullTimeEmployees",
            "phone", "address", "city", "state", "zip", "dcfDiff", "dcf", "ipoDate"
        ]

        for profile in data:
            # Ensure all columns have a value (use None for missing fields)
            values = [
                None if profile.get(col, None) == "" else profile.get(col, None) for col in columns
            ]

            insert_query = f"""
            INSERT INTO indian_company_profiles (
                {', '.join(columns)}
            ) VALUES ({', '.join(['%s'] * len(columns))})
            ON CONFLICT (symbol) DO NOTHING;
            """
            cur.execute(insert_query, values)

        conn.commit()
        cur.close()
        conn.close()
        print("Data successfully pushed to PostgreSQL.")
    except Exception as e:
        print(f"Error pushing data to PostgreSQL: {e}")

if __name__ == "__main__":
    # Step 1: Fetch Indian company symbols
    symbols = client.fetch_stock_list()
    indian_exchanges = ["NSE", "BSE"]
    symbols = [stock["symbol"] for stock in symbols if stock.get("exchangeShortName") in indian_exchanges]
    print(f"Total Indian Companies Found: {len(symbols)}")

    # **No limitation on symbols—process all 6000+ stocks**
    print("Processing all symbols...")

    # Step 2: Fetch company profiles
    profiles = fetch_company_profiles(symbols)

    # Step 3: Save profiles to CSV
    # save_to_csv(profiles, "indian_company_profiles.csv")

    # Step 4: Push profiles to PostgreSQL
    push_to_postgres(profiles)


