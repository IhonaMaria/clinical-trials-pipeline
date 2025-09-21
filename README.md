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

### Airflow DAG (`docker/airflow/dags/clinical_pipeline_dag.py`)
This orchestration layer manages the complete pipeline execution:

**DAG Structure:**
1. **Data Ingestion**: Fetches new trials from API
2. **Silver Processing**: Runs dbt silver layer transformations
3. **Gold Processing**: Runs dbt gold layer transformations

The DAG executes on demand (but could be easily scheduled weekly or daily for example)

**Dependencies:**
```
fetch_trials → dbt_run_silver → dbt_run_gold
```

## Best Practices

- **Data validation**: Built-in dbt tests and constraints
- **Modular design**: Separated concerns across layers
- **Configuration management**: Environment-specific settings
- **Documentation**
- **Version control**: Git-based change management

### Infrastructure
- **Containerization**
- **Resource isolation**: Dedicated containers for each service
- **Persistent storage**: Data persistence across container restarts

## Improvements and Considerations

### Immediate Enhancements
- **dbt Documentation**: Auto-generate model documentation and lineage
- **SQLFluff**: Implement SQL linting for code quality
- **Enhanced Testing**: Add extra dbt tests and Airflow DAG validation
- **Environment Configuration**: Implement `.env` files for production deployment

### Production Readiness
- **Pipeline Monitoring**: Implement alerting and health checks
- **Failure Handling**
- **Scalability**: 
  - Horizontal scaling for high-volume ingestion
  - Partitioning strategies for large datasets
  - Caching layers for frequently accessed data

### Data Expansion
- **Additional Data Sources**: 
  - FDA drug approval data
  - Medical literature APIs
  - Real-world evidence databases
- **Advanced Analytics**:
  - Machine learning model integration
  - Predictive analytics for trial outcomes
  - Real-time data streaming capabilities

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Git

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd clinical-trials-pipeline

# Start the pipeline
cd docker
docker-compose up -d

# Access Airflow UI
open http://localhost:8080
# Username: airflow, Password: airflow

# Run the pipeline manually in Airflow UI
```

### Development Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run dbt locally
cd dbt
dbt deps
dbt run
```

## BONUS QUESTIONS

### Why This Architecture?
This medallion architecture provides:
- **Data Quality**: Progressive data cleaning and validation
- **Flexibility**: Easy to modify transformations without affecting raw data
- **Auditability**: Complete data lineage and change tracking
- **Performance**: Optimized queries at each layer

### Scalability Considerations
- **API Rate Limiting**: Implement exponential backoff and request queuing
- **Database Optimization**: Indexing strategies and query optimization
- **Resource Management**: Container resource limits and auto-scaling
- **Data Partitioning**: Time-based partitioning for large datasets

### Future Enhancements
- **Real-time Processing**: Stream processing for live trial updates
- **ML Integration**: Predictive models for trial success rates
- **API Development**: RESTful APIs for data access
- **Visualization**: Interactive dashboards and reporting tools


# VISUALIZATION

### For Demo Purposes
1. **Start main pipeline**: `cd docker && docker-compose up -d`
2. **Run data ingestion**: Execute the Airflow DAG
3. **Start dashboard**: `cd metabase && docker-compose up -d`
4. **Show results**: Navigate to http://localhost:3000

### Prerequisites
- Docker and Docker Compose
- Your main clinical trials pipeline running (for data)

### 1. Start the Dashboard
```bash
cd metabase
docker-compose up -d
```

### 2. Access Metabase
- **URL**: http://localhost:3000
- **First-time setup**: Create admin account
- **Database connection**: Already configured to connect to PostgreSQL