# Orchestration Airfow DAG

# 1. Runs the Python Script to pull trials from the API into Postgres
# 2. Runs silver transformations
# 3. Runs gold transformations

from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime
from airflow.utils import timezone 

default_args = {
    "start_date": timezone.datetime(2024, 1, 1)  # aware (UTC by default)
}

preamble = r"""
set -euo pipefail # To handle errors 
export DBT_PROFILES_DIR=/home/airflow/.dbt # Tells dbt where to find profiles.yml
export DBT_TARGET_PATH=/tmp/dbt_target
export DBT_LOG_PATH=/tmp/dbt_logs
mkdir -p "$DBT_TARGET_PATH" "$DBT_LOG_PATH"
dbt --version
"""

with DAG(
    dag_id="clinical_trials_pipeline", # Unique name we can see on the UX/UI
    description="Ingest and process clinical trial data",
    schedule=None,          # manual runs
    tags=["clinical", "dbt", "pipeline"],
    default_args=default_args,
) as dag:

    # 1) Ingest raw data into Postgres bronze.raw_trials
    ingest_data = BashOperator(
        task_id="fetch_trials",
        bash_command=r"""
          set -euo pipefail
          python /usr/app/ingestion/fetch_new_trials.py
        """,
    )
    
     # 2) Build SILVER models (cleaned/normalized tables)
    dbt_run_silver = BashOperator(
        task_id="dbt_run_silver",
        bash_command=preamble + r"""
          cd /usr/app
          dbt run --select silver --threads 4 \
            --target-path "$DBT_TARGET_PATH" \
            --log-path "$DBT_LOG_PATH"
        """,
    )

    # 3) Build GOLD models (analytics-ready marts for Metabase)
    dbt_run_gold = BashOperator(
        task_id="dbt_run_gold",
        bash_command=preamble + r"""
          cd /usr/app
          dbt run --select gold --threads 4 \
            --target-path "$DBT_TARGET_PATH" \
            --log-path "$DBT_LOG_PATH"
        """,
    )

    ingest_data >> dbt_run_silver >> dbt_run_gold
