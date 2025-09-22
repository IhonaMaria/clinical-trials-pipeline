FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Europe/Madrid

# System deps for psycopg2 & build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Python deps: dbt + utilities
RUN pip install --no-cache-dir \
    dbt-core==1.9.1 dbt-postgres==1.9.1 \
    requests==2.32.3 psycopg2-binary==2.9.9 \
    tenacity==8.2.3 apscheduler==3.10.4

WORKDIR /app
# copy the orchestrator
COPY orchestrate.py /app/orchestrate.py

# Default command
CMD ["python", "/app/orchestrate.py"]
