from dotenv import load_dotenv
import os

import pandas as pd
import psycopg2
from datetime import datetime
from psycopg2.extras import execute_values

#load_dotenv()
load_dotenv(dotenv_path="../docker/.env")

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")

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

# Connection config
SHARD_DB_CONFIG = {
    'shard1': {'dbname': 'shard1_db', 'user': user, 'password': password, 'host': 'localhost', 'port': int(os.getenv("PG_SHARD1_PORT"))},
    'shard2': {'dbname': 'shard2_db', 'user': user, 'password': password, 'host': 'localhost', 'port': int(os.getenv("PG_SHARD2_PORT"))},
    'shard3': {'dbname': 'shard3_db', 'user': user, 'password': password, 'host': 'localhost', 'port': int(os.getenv("PG_SHARD3_PORT"))},
    'shard4': {'dbname': 'shard4_db', 'user': user, 'password': password, 'host': 'localhost', 'port': int(os.getenv("PG_SHARD4_PORT"))},
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