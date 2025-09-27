# Clinical Trials Data Pipeline

This is a comprehensive data engineering pipeline that ingests, transforms, and orchestrates clinical trial data from the ClinicalTrials.gov API using modern data stack technologies.

This proposed pipeline:
- Fetches clinical trial data from the ClinicalTrials.gov API
- Implements a medallion architecture for data quality and governance
- Uses dbt for data transformation with SQL-based modeling
- Orchestrates the entire pipeline using a Python code. An Airflow DAG example is also provided, but this is left for future improvements. 
- Stores data in PostgreSQL with proper schema organization

Additionally, a visualization layer with Metabase is built to answer analytical questions.

## TECH STACK + WORKFLOW

<img width="1413" height="645" alt="image" src="https://github.com/user-attachments/assets/8d13e0ca-2667-4936-948d-b7f4a3aa062c" />

Core Technologies
- **Data Source**: ClinicalTrials.gov API v2
- **Database**: PostgreSQL 15
- **Data Transformation**: dbt (Data Build Tool) 1.9.1
- **Orchestration**: Python code (Airflow proposed for future releases)
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
- Has built-in data quality [tests](https://medium.com/@ihona.correadecabo/getting-started-with-dbt-tests-af10fdd6fc45)
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
The entire pipeline was orchestrated with a single Python script inside Docker. It ingests the data from the API into the bronze layer (running the fetch_new_trials code), and then runs dbt silver and gold models.This kept the project simple, portable, and conflict-free. Airflow was attempted, and example DAG can be found as a result here: clinical-trials-pipeline\docker\airflow\dags\clinical_pipeline_dag.py. Due to time constrains, it was not feasible in the end. However, in production environments Airflow shines for scheduling and monitoring complex workflows. 


## FUTURE IMPROVEMENTS AND CONSIDERATIONS
- Documentation of dbt models, macros, etc 
- Use [SQLFluff](https://medium.com/@ihona.correadecabo/linting-dbt-projects-with-sqlfluff-119be9e3742a)
 for consistency
- Do more dbt tests
- Orchestrate using Airflow
- Use a .env in a production setting
- Monitor the pipeline
- Connect to other data sources

# VISUALIZATION
I containerized Metabase (a BI tool) with Docker to spin up a UI and build quick visualizations answering questions like trials by study type, geographic distribution of trials, etc. I chose metabase because it is free, easy to set up and you can build the visualizations on top of the database (in this case the gold layer). If you happen to change the gold layer logic, the visualizations update automatically.

Here is a screenshot of the result:
<img width="998" height="935" alt="dashboard" src="https://github.com/user-attachments/assets/d5c786bf-ee9e-471f-b53c-49d485c1a691" />


# BONUS QUESTIONS

#### Scalability: How would you modify your solution to handle 100x more data volume?
To handle a much larger data volume, I would:
- Build incremental models in dbt, so only new or updated data is processed — not the whole dataset.
- Increase parallelism by running dbt with multiple threads.
- Move from Postgres to a cloud-based data warehouse (like BigQuery or Snowflake) to benefit from auto-scaling compute and storage.
- Use partitioned tables and clustering strategies to optimize query performance on large datasets.

#### Data Quality: What additional data validation rules would you implement for clinical trial data?
- Add more dbt tests, for instance: not null constraints for essential fields like study_type, start_date, or condition.
- Check with domain experts why a certain field is always null, for instance.
  
#### Compliance: If this were a GxP environment, what additional considerations would you need?
- Data lineage
- Access control and user roles, with proper authentication and authorization.
- Add CI/CD practices
- Robust validation procedures of the data and the pipeline
  
#### Monitoring: How would you monitor this pipeline in production?
- Use Airflow's built-in monitoring (logs, email alerts, DAG failure notifications).
- Implement logging and metrics (number of rows ingested, data freshness).
- Set up a dashboard to visualize pipeline health and trends.
  
#### Security: What security measures would you implement for sensitive clinical data?
- Follow least privilege principles: restrict access to only what's necessary.
- Create role-based permissions in the database.
- Anonymization of sensitive fields. 
- Avoid hardcoding secrets — use .env files and secret managers.
- Encrypt sensitive data at rest and in transit.
- Set up credential rotation policies to avoid stale access.
  
# HOW TO SET THIS UP LOCALLY

For the data pipeline:

1. You need to have Docker Desktop and DBeaver (optional, if you want to see the tables).
2. Clone this repository in your folder.
3. Go to the docker folder inside the project: cd docker
4. Start Postgres: docker compose up -d postgres
5. Install Dbeaver, go to the interface and select "new database connection". Choose Postgres and then fill the connection details:
<img width="1227" height="677" alt="image" src="https://github.com/user-attachments/assets/4984a8da-4349-4aa1-9979-c9cded292cbf" />




<img width="687" height="722" alt="image" src="https://github.com/user-attachments/assets/fe935d17-61e0-408c-adaf-20f4657f87db" />

- database: clinical_trials
- Name: user
- Password: password
- Port: 5432

6. Run the data pipeline once: **docker compose run --rm orchestrator python /app/orchestrate.py --once**
7. You can see the created tables in Dbeaver, for instance: select * from clinical_trials.gold.gld_interventions

For the visualization:

1. Go to the metabase folder.
2. Execute docker compose up
3. You will need to register and establish the connection with the gold layer.

Note that you won't be able to reproduce the visualization since it will be linked to my metabase account. 

# FINAL NOTES
Time spent: Around 10 hours

-  1h for architecture planning, designing
-  1h for API connection, data exploration
-  2 h for data modelling and setting up dbt
-  3 h for the orchestration
-  1h for visualization
-  2h documenting the project

ChatGPT and Cursor were used to accelerate the process.
