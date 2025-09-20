from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {"start_date": datetime(2024, 1, 1)}

with DAG(
    dag_id="clinical_trials_pipeline",
    description="Ingest and process clinical trial data",
    schedule="@daily",          # or None for manual runs
    catchup=False,
    default_args=default_args,
    tags=["clinical", "dbt", "pipeline"],
) as dag:

    # 1) Ingest from API into Postgres (bronze)
    ingest_data = BashOperator(
        task_id="fetch_trials",
        bash_command=r"""
          set -euo pipefail
          python /usr/app/ingestion/fetch_new_trials.py
        """,
    )

    # tiny preamble to avoid dbt cache/permission issues
    preamble = r"""
      set -euo pipefail
      export DBT_PROFILES_DIR=/home/airflow/.dbt
      export DBT_TARGET_PATH=/tmp/dbt_target
      export DBT_LOG_PATH=/tmp/dbt_logs
      mkdir -p "$DBT_TARGET_PATH" "$DBT_LOG_PATH"
      # ensure no stale cache on bind mount
      rm -rf /usr/app/target || true
      dbt --version
    """

    # 2) Transform to silver
    dbt_run_silver = BashOperator(
        task_id="dbt_run_silver",
        cwd="/usr/app",   # where your dbt_project.yml lives
        bash_command=preamble + r"""
          dbt run --select silver --threads 4 \
            --target-path "$DBT_TARGET_PATH" \
            --log-path "$DBT_LOG_PATH"
        """,
    )

    # 3) Transform to gold
    dbt_run_gold = BashOperator(
        task_id="dbt_run_gold",
        cwd="/usr/app",
        bash_command=preamble + r"""
          dbt run --select gold --threads 4 \
            --target-path "$DBT_TARGET_PATH" \
            --log-path "$DBT_LOG_PATH"
        """,
    )

    ingest_data >> dbt_run_silver >> dbt_run_gold
