# docker/Dockerfile
FROM apache/airflow:2.8.4-python3.11  

USER root

# Install OS package 
RUN apt-get update && apt-get install -y --no-install-recommends git \
 && rm -rf /var/lib/apt/lists/*

USER airflow
# Add Python deps needed by the pipeline
RUN pip install --no-cache-dir --upgrade "pip<24" "setuptools<70" wheel
RUN pip install --no-cache-dir "dbt-postgres==1.9.1" "psycopg2-binary>=2.9" "requests>=2.31"

# Prepare folders used by dbt
# ensure pip user is on path
# Tells where dbt can find profiles, where to write artifacts and logs, etc
RUN mkdir -p /tmp/dbt_target /tmp/dbt_logs  
ENV PATH="/home/airflow/.local/bin:${PATH}"
ENV DBT_PROFILES_DIR="/home/airflow/.dbt"
ENV DBT_TARGET_PATH="/tmp/dbt_target"
ENV DBT_LOG_PATH="/tmp/dbt_logs"
