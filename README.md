# Clinical Trials Data Pipeline

This is a comprehensive data engineering pipeline that ingests, transforms, and orchestrates clinical trial data from the ClinicalTrials.gov API using modern data stack technologies.

## Overview

This project demonstrates a production-ready data pipeline that:
- Fetches clinical trial data from the ClinicalTrials.gov API
- Implements a medallion architecture for data quality and governance
- Uses dbt for data transformation with SQL-based modeling
- Orchestrates the entire pipeline using Apache Airflow
- Stores data in PostgreSQL with proper schema organization

## TECH STACK + WORKFLOW

### Core Technologies
- **Data Source**: ClinicalTrials.gov API v2
- **Database**: PostgreSQL 15
- **Data Transformation**: dbt (Data Build Tool) 1.9.1
- **Orchestration**: Apache Airflow 2.8.4
- **Containerization**: Docker & Docker Compose
- **Language**: Python and SQL

### Architecture Flow
```
ClinicalTrials.gov API → Python Ingestion → PostgreSQL (Bronze) → dbt (Silver/Gold) → Analytics Ready Data
                                    ↓
                              Airflow Orchestration
```

## INGESTION

### API Integration
The pipeline connects to the **ClinicalTrials.gov API v2** (`https://clinicaltrials.gov/api/v2/studies`) which provides:
- Comprehensive clinical trial metadata
- Structured JSON responses
- Access to trial status, phases, and enrollment data

### Python Code (`ingestion/fetch_new_trials.py`)
The ingestion script implements:
- **Pagination handling**: Uses `nextPageToken` to fetch large datasets efficiently
- **Data extraction**: Parses complex nested JSON to extract key trial attributes:
  - Trial identification (NCT ID, title)
  - Study design (type, phase)
  - Status tracking (overall status, start and end dates)
  - Clinical details (conditions, interventions, countries)
- **Database integration**: Direct PostgreSQL insertion

Key features:
- Configurable batch size (default: 1000 trials)
- Error handling with detailed API response logging
- Upsert logic to handle duplicate trials gracefully

## DATA TRANSFORMATION

### Data Analysis & Transformation Strategy
The raw API data required significant transformation to be analytics-ready:

**Raw Data Challenges:**
- Inconsistent date formats (YYYY, YYYY-MM, YYYY-MM-DD)
- Placeholder values ('NA', 'N/A', 'UNKNOWN', 'NULL')
- Mixed data types and missing values
- Nested JSON structures flattened into delimited strings (, ;)

The raw data ingested was brought into a bronze schema in Postgres and then it was modeled with dbt.

**Transformation Solutions:**
- **Date standardization**: Regex-based parsing for partial dates
- **Data cleaning**: Systematic nullification of placeholder values
- **Type conversion**: Proper data type casting and validation
- **Normalizing fields**: Conditons, countries and interventions were exploded for each NCT ID.

### Why dbt?
dbt was chosen for data transformation because:
- Leverages existing SQL skills
- Has Git-based model management
- Has built-in data quality tests
- Offers modularity through reusable models and macros
- It can handle incremental processing (although not used here, but good in production environments and for large datasets)

### dbt Organization
```
dbt/
├── models/
│   ├── silver/          # Cleaned data
│   │   ├── slv_processed_trials.sql
│   │   ├── slv_conditions.sql
│   │   ├── slv_countries.sql
│   │   └── slv_interventions.sql
│   └── gold/            # Business-ready analytics tables
│       ├── gld_enriched_trials.sql
│       ├── gld_conditions.sql
│       ├── gld_countries.sql
│       └── gld_interventions.sql
├── seeds/               # Helper data for visualization
│   └── country_codes.csv
└── macros/              # Reusable SQL functions
    └── genrate_schema_name.sql
```

## DATA MODELLING

### Medallion Architecture
The pipeline implements a **medallion architecture** with three layers:

#### Bronze Layer (Raw Data)
- **Purpose**: Store raw, unprocessed data exactly as received
- **Schema**: `bronze.raw_trials`
- **Characteristics**: 
  - Preserves original data structure
  - Minimal transformation (JSON flattening only)

#### Silver Layer (Cleaned Data)
- **Purpose**: Clean and standardized data
- **Schema**: `silver.*`
- **Transformations**:
  - Date parsing and standardization
  - Null handling and data type conversion
  - Business rule application (e.g., phase logic)
  - Data quality validation

#### Gold Layer (Analytics Ready)
- **Purpose**: "Business-ready" datasets for analytics and reporting
- **Schema**: `gold.*`
- **Features**:
  - Calculated metrics (study duration, for example)
  - Ready for visualization tools

The gold layer implements a **star schema** pattern:
- **Fact Table**: `gld_enriched_trials` (central trial data)
- **Dimension Tables**: 
  - `gld_conditions` (trial conditions)
  - `gld_countries` (geographic data)
  - `gld_interventions` (treatment information)

This design enables:
- Fast analytical queries
- Easy data exploration
- Scalable reporting solutions

## DATA ORCHESTRATION

DAG to run the python ingestion an dbt into postgres

## best practices

## Improvements and considerations
-document dbt
-sqlfluff
-more tests, include the test on airflow dag
.env in case we deploy to production
-pipeline monitoring
-how to handle failure? 
-ingestion of other data types

# BONUS QUESTIONS
