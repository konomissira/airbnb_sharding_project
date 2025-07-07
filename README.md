# Airbnb Listings – PostgreSQL Sharding with Grafana Dashboard

This project showcases a professional level data engineering solution using **PostgreSQL sharding** across four containers, integrated with **Grafana** for real-time monitoring and dashboards. The dataset is based on Airbnb listings in London. The project has been successfully deployed to AWS using **CloudFormation**, **EC2**, **Elastic IP**, and **SSH access via key pairs**. The deployment simulates a production-ready environment where PostgreSQL shards run inside Docker containers on an EC2 instance.

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
├── infrastructure/
│   ├── ec2-sharded-postgres-stack.yml     # CloudFormation Template
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

Because `/data` folder is in `.gitignore` file to avoid slow Git pushes, you must manually download and clean the dataset here's the link: https://insideairbnb.com/fr/get-the-data/

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

## Deployment to AWS (Cloud)

### Pre-requisites

-   AWS account (Free Tier eligible)
-   AWS CLI configured with your IAM user
-   An EC2 key pair (RSA format, `.pem` file)
-   GitHub repo cloned locally
-   Docker & Docker Compose installed

### 1. Create and Attach IAM Permissions

Make sure your IAM user has the following permissions:

-   `AmazonEC2FullAccess`
-   `CloudFormationFullAccess`

### 2. Create a Key Pair

Create a key pair to SSH into your EC2 instance:

```bash
aws ec2 create-key-pair --key-name kono-key \
  --query 'KeyMaterial' --output text > kono-key.pem

chmod 400 kono-key.pem
```

Move the .pem file from downloads folder to your project root folder:

```bash
mv ~/Downloads/kono-key.pem ./
```

⚠️ **Important:**  
Do **not** push the .pem (e.g. kono-key.pem) file to GitHub. Add it to `.gitignore`:

```bash
# .gitignore
kono-key.pem
```

### 3. Update AMI ID for Your Region

The default AMI ID may not exist in `eu-west-1`. To get the latest Ubuntu AMI:

```bash
aws ec2 describe-images \
  --owners 099720109477 \
  --filters 'Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*' \
  --query 'Images[*].[ImageId,CreationDate]' \
  --output text \
  --region eu-west-1 | sort -k2 -r | head -n 1
```

Copy the AMI ID (e.g., `ami-0dc0a.......`) and replace it in your CloudFormation template file:

```yaml
infrastructure/ec2-sharded-postgres-stack.yml
```

### 4. Deploy CloudFormation Stack

Run the command below to launch the infrastructure:

```bash
aws cloudformation create-stack \
  --stack-name postgres-shard-stack \
  --template-body file://infrastructure/ec2-sharded-postgres-stack.yml \
  --parameters ParameterKey=KeyName,ParameterValue=kono-key \
  --capabilities CAPABILITY_NAMED_IAM \
  --region eu-west-1
```

You should see a `CREATE_COMPLETE` message once deployed.

### 5. Elastic IP Setup

An Elastic IP was associated to ensure the EC2 instance always has the same IP address:

```
Elastic IP used: 54.247.109.226
```

### 6. SSH into the EC2 Instance

```bash
ssh -i kono-key.pem ubuntu@54.247.X.X
```

### 7. Run the Containers on EC2

Once connected to your instance, navigate to the project folder and run:

```bash
docker compose up -d
```

This will start the following services:

-   `pg_shard1`, `pg_shard2`, `pg_shard3`, `pg_shard4`
-   `pgAdmin` (on port 5050)
-   `Grafana` (on port 3000)

### ✅ Reminder: Stop EC2 to Avoid Charges

```bash
aws ec2 stop-instances --instance-ids i-YourInstanceID e.g.0c6beb07XXXXXXXX --region eu-west-1
```

You can confirm it’s stopped with:

```bash
aws ec2 describe-instances --instance-ids i-0c6beb07XXXXXXXX --region eu-west-1 \
  --query 'Reservations[*].Instances[*].State.Name' --output text
```

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
