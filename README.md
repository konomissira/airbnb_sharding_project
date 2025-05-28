# Airbnb Listings – PostgreSQL Sharding with Grafana Dashboard

This project showcases a professional level data engineering solution using **PostgreSQL sharding** across four containers, integrated with **Grafana** for real-time monitoring and dashboards. The dataset is based on Airbnb listings in London.

## 📁 Project Structure

```
├── data/                      # (Git-ignored) Raw + cleaned Airbnb data
├── docker/                    # Docker-related setup
│   ├── shard1/init.sql        # Shard 1 schema
│   ├── shard2/init.sql        # Shard 2 schema
│   ├── shard3/init.sql        # Shard 3 schema
│   ├── shard4/init.sql        # Shard 4 schema
│   ├── docker-compose.yml     # Multi-service setup: shards, pgAdmin,
│   └── .env                   # Stores credentials and ports
├── notebooks/
│   ├── eda_analysis.ipynb     # EDA Analysis to understand the data
    ├── clean_data.ipynb       # Cleans and saves Airbnb data
├── src/
│   ├── shard_router_v1.py     # Routes cleaned data to appropriate shard using .env
├── .gitignore
└── README.md
```

## Project Goals

-   **Shard Airbnb listings** by borough into 4 PostgreSQL instances
-   **Route** the cleaned data programmatically to correct shards
-   **Visualise insights** in Grafana with PostgreSQL data sources
-   **Use environment variables** for security and config
-   **Avoid committing large files** by excluding `/data` from Git

## 💻 Tech Stack

-   **Programming**: Python (`pandas`, `psycopg2`, `dotenv`)
-   **Databases**: PostgreSQL (sharded across 4 Docker containers)
-   **Containerisation & Orchestration**: Docker, Docker Compose
-   **Monitoring & Visualisation**: Grafana (connected to PostgreSQL shards)
-   **Database Admin UI**: pgAdmin
-   **Security**: Environment variables via `.env` (for credentials and configuration)
-   **Version Control**: Git, GitHub (with `.gitignore` to exclude large files and data)

## 📦 Setup Instructions

### 1. Clone the repo

```bash

git clone https://github.com/konomissira/airbnb_sharding_project.git
cd airbnb_sharding_project/docker
```

### 2. Create `.env` file in `docker/`

```ini
# .env file
POSTGRES_USER=YourPostgreUsername
POSTGRES_PASSWORD=YourPostgrePassword

PG_SHARD1_PORT=5433
PG_SHARD2_PORT=5434
PG_SHARD3_PORT=5435
PG_SHARD4_PORT=5436

PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=YourPgadminPassword

GRAFANA_ADMIN_USER=YourGrafanaUsername
GRAFANA_ADMIN_PASSWORD=YourGrafanaPassword
```

### 3. Download and clean the dataset

Because `/data` is `.gitignore`-d to avoid slow Git pushes, you must manually download and clean the dataset here's the link: https://insideairbnb.com/fr/get-the-data/

Also, you must have Jupyter Notebook in order to run eda_analysis.ipynb and clean_data.ipynb which will clean and save the clean data into the data folder.

### 4. Spin up the containers:

You must have docker installed in your computer.

```bash
cd ../docker
docker compose up -d
```

## 🗃️ Registering Shards in pgAdmin

-   Access pgAdmin at this url: http://localhost:5050
-   Use credentials from `.env`

When registering each shard server:

-   **Host**: `pg_shard1`, `pg_shard2`, etc.
-   **Port**: `5432`
-   **Username**: from `.env`
-   **Password**: from `.env`

## Load Data to PostgreSQL Shards

```bash
cd src
python3 shard_router_v1.py
```

This script reads `cleaned_airbnb_listings.csv`, maps each borough to its correct shard, and inserts records using `psycopg2` and `execute_values`.

## 📊 Grafana Dashboard

-   Access Grafana at this url: http://localhost:3000
-   Use credentials from `.env`

### Add PostgreSQL Data Sources

Repeat this step 4 times (one per shard):

-   **Name**: `shard1`, `shard2`, etc.
-   **Host**: `pg_shard1:5432`
-   **Database**: `shard1_db`, etc.
-   **User**: from `.env`
-   **Password**: from `.env`

## SQL Query Examples

```sql
-- Number of listings per room type
SELECT room_type, COUNT(*) FROM listings GROUP BY room_type;

-- Average price per borough
SELECT neighbourhood, AVG(price) FROM listings GROUP BY neighbourhood;
```

## ✅ Key Highlights

-   📂 Modular Docker setup for each shard
-   🔒 Environment variables used for all credentials
-   Clean, professional code with clear structure
-   📉 Interactive visual analytics via Grafana

## Future Improvements

-   Integrate Apache Airflow
-   Add automated test scripts for ETL validation
-   Provision Grafana panels programmatically

## License

-   This project is licensed under the MIT License.
-   You are free to use, modify, and distribute this software with proper attribution.

## Author

-   **Name:** Mahamadou
-   **Role:** Data Engineer
