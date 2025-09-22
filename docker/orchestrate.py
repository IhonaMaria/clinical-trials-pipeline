# Orchestrates the end-to-end pipeline:
# 1) INGEST: runs a Python script that pulls latest clinical trials into Postgres (bronze schema)
# 2) TRANSFORM: runs dbt models for silver (cleaned) and gold (analytics-ready) layers

import os, subprocess, sys

INGESTION_ENTRYPOINT = "/usr/app/ingestion/fetch_new_trials.py"
DBT_PROJECT_DIR      = "/usr/app"              # contains dbt_project.yml
DBT_PROFILES_DIR     = "/usr/app/profiles"     # contains profiles.yml
DBT_TARGET           = "dev"

# Where to save artifacts
DBT_LOG_PATH         = "/tmp/dbt_logs"
DBT_TARGET_PATH      = "/tmp/dbt_target"

def run(cmd, **kwargs):
  """
  Helper to run shell commands with nice logging and 'fail fast' behavior.
  subprocess.run(..., check=True) will raise CalledProcessError if the command fails.
  """
  print(f"\n→ Running: {' '.join(cmd)}")
  subprocess.run(cmd, check=True, **kwargs)
  print("✓ Done.")

def main():
  # Ensure dbt dirs exist
  os.makedirs(DBT_LOG_PATH, exist_ok=True)
  os.makedirs(DBT_TARGET_PATH, exist_ok=True)

  run(["python", "-u", INGESTION_ENTRYPOINT]) # 1) INGEST: pull raw trials and load them into Postgres 


  # 2) TRANSFORM with dbt
  # We pass configuration via environment variables and run from the project dir (cwd),
  env = os.environ.copy()
  env["DBT_PROFILES_DIR"] = DBT_PROFILES_DIR
  env["DBT_LOG_PATH"]     = DBT_LOG_PATH
  env["DBT_TARGET_PATH"]  = DBT_TARGET_PATH

  run(["dbt", "deps"], cwd=DBT_PROJECT_DIR, env=env) # Downloads required dbt packages needed 
  # Build SILVER models
  run(["dbt", "run", "--select", "silver", "--threads", "4", "--target", DBT_TARGET],
      cwd=DBT_PROJECT_DIR, env=env)
  # Build GOLD models
  run(["dbt", "run", "--select", "gold", "--threads", "4", "--target", DBT_TARGET],
      cwd=DBT_PROJECT_DIR, env=env)

if __name__ == "__main__":
  try:
    main()
    print("\nPipeline finished successfully.")
  except subprocess.CalledProcessError as e:
    print(f"\n Step failed with exit code {e.returncode}", file=sys.stderr)
    sys.exit(e.returncode)
  except Exception as e:
    print(f"\n Unexpected error: {e}", file=sys.stderr)
    sys.exit(1)
