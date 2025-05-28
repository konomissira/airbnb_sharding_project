import pandas as pd
import psycopg2
from datetime import datetime
from psycopg2.extras import execute_values

# Borough to shard mapping
NEIGHBOURHOOD_SHARD_MAP = {
    'Camden': 'shard1',
    'Hackney': 'shard1',
    'Islington': 'shard1',
    'Westminster': 'shard1',
    'Tower Hamlets': 'shard2',
    'Lambeth': 'shard2',
    'Southwark': 'shard2',
    'Ealing': 'shard3',
    'Brent': 'shard3',
    'Barnet': 'shard3',
    'Croydon': 'shard4',
    'Bromley': 'shard4',
    'Bexley': 'shard4',
}

# Connection config if you want to test it locally before integrate with .env
SHARD_DB_CONFIG = {
    'shard1': {'dbname': 'shard1_db', 'user': 'YourUSerName', 'password': 'YourPassWord', 'host': 'localhost', 'port': 5433},
    'shard2': {'dbname': 'shard2_db', 'user': 'YourUSerName', 'password': 'YourPassWord', 'host': 'localhost', 'port': 5434},
    'shard3': {'dbname': 'shard3_db', 'user': 'YourUSerName', 'password': 'YourPassWord', 'host': 'localhost', 'port': 5435},
    'shard4': {'dbname': 'shard4_db', 'user': 'YourUSerName', 'password': 'YourPassWord', 'host': 'localhost', 'port': 5436},
}

# Load cleaned data
data = pd.read_csv("../data/cleaned_airbnb_listings.csv")

# Convert date column
data['last_review'] = pd.to_datetime(data['last_review'], errors='coerce')

# Group rows by shard
shard_data = {'shard1': [], 'shard2': [], 'shard3': [], 'shard4': []}

for _, row in data.iterrows():
    shard = NEIGHBOURHOOD_SHARD_MAP.get(row['neighbourhood'])
    if shard:
        shard_data[shard].append(tuple(row.where(pd.notnull(row), None))) # convert row to tuple, replacing NaNs with None

# Insert into each shard
for shard, rows in shard_data.items():
    if not rows:
        continue

    config = SHARD_DB_CONFIG[shard]
    print(f"Inserting {len(rows)} records into {shard}...")

    with psycopg2.connect(**config) as conn:
        with conn.cursor() as cur:
            query = """
                INSERT INTO listings (
                    id, name, host_id, host_name, neighbourhood, latitude, longitude,
                    room_type, price, minimum_nights, number_of_reviews, last_review,
                    reviews_per_month, calculated_host_listings_count, availability_365,
                    number_of_reviews_ltm
                ) VALUES %s
                ON CONFLICT (id) DO NOTHING;
            """
            execute_values(cur, query, rows)

print("Data loaded into shards successfully.")
