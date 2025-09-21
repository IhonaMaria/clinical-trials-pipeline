# Clinical Trials Data Pipeline

This is a comprehensive data engineering pipeline that ingests, transforms, and orchestrates clinical trial data from the ClinicalTrials.gov API using modern data stack technologies.

This proposed pipeline:
- Fetches clinical trial data from the ClinicalTrials.gov API
- Implements a medallion architecture for data quality and governance
- Uses dbt for data transformation with SQL-based modeling
- Orchestrates the entire pipeline using Apache Airflow
- Stores data in PostgreSQL with proper schema organization

Additionally, a visualization layer with Metabase is built to answer analytical questions.

## TECH STACK + WORKFLOW

<img width="1413" height="645" alt="image" src="https://github.com/user-attachments/assets/8d13e0ca-2667-4936-948d-b7f4a3aa062c" />

Core Technologies
- **Data Source**: ClinicalTrials.gov API v2
- **Database**: PostgreSQL 15
- **Data Transformation**: dbt (Data Build Tool) 1.9.1
- **Orchestration**: Apache Airflow 2.8.4
- **Containerization**: Docker & Docker Compose
- **Language**: Python and SQL

## INGESTION

### API Integration
The pipeline connects to the **ClinicalTrials.gov API v2** (`https://clinicaltrials.gov/api/v2/studies`) which provides:
- Comprehensive clinical trial metadata
- Structured JSON responses
- Access to trial status, phases, and enrollment data

### Python Code (`ingestion/fetch_new_trials.py`)
The ingestion script implements:
- **Data extraction**: Parses complex nested JSON to extract key trial attributes:
  - Trial identification (NCT ID, title)
  - Study design (type, phase)
  - Status tracking (overall status, start and end dates)
  - Clinical details (conditions, interventions, countries)
- **Database integration**: Direct PostgreSQL insertion

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
An Airflow DAG was used to run the python ingestion and dbt layers into postgres.
I chose it to try to mymic a production environment. It reliably schedules and orders the pipeline, handles retries and provides built-in monitoring.

## Best practices used
- tests for validation
- separations of services with docker


## Improvements and considerations
- Documentation of dbt models, macros, etc 
- Use [SQLFluff](https://medium.com/@ihona.correadecabo/linting-dbt-projects-with-sqlfluff-119be9e3742a)
 for consistency
- Do more dbt tests
- Test the DAG
- Use a .env in a production setting
- Monitor the pipeline
- Connect to other data sources

# VISUALIZATION
I containerized Metabase (a BI tool) with Docker to spin up a UI and build quick visualizations answering questions like trials by study type, geographic distribution of trials, etc. I chose metabase because it is free, easy to set up and you can build the visualizations on top of the database (in this case the gold layer). If you happen to change the gold layer logic, the visualizations update automatically.

Here is a screenshot of the result:
<img width="998" height="935" alt="dashboard" src="https://github.com/user-attachments/assets/d5c786bf-ee9e-471f-b53c-49d485c1a691" />


# BONUS QUESTIONS




# HOW TO SET THIS UP LOCALLY



