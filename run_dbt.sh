#!/bin/bash

# Run dbt commands inside Docker container
echo "Running dbt debug..."
docker-compose -f docker/docker-compose.yml run --rm dbt /usr/local/bin/dbt debug --profiles-dir /root/.dbt

echo "Running dbt models..."
docker-compose -f docker/docker-compose.yml run --rm dbt /usr/local/bin/dbt run --profiles-dir /root/.dbt --select silver
