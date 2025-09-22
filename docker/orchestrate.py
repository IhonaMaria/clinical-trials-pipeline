#!/usr/bin/env python3
import os, subprocess, sys

INGESTION_ENTRYPOINT = "/usr/app/ingestion/fetch_new_trials.py"
DBT_PROJECT_DIR      = "/usr/app"              # contains dbt_project.yml
DBT_PROFILES_DIR     = "/usr/app/profiles"     # contains profiles.yml
DBT_TARGET           = "dev"

DBT_LOG_PATH         = "/tmp/dbt_logs"
DBT_TARGET_PATH      = "/tmp/dbt_target"

def run(cmd, **kwargs):
  print(f"\n→ Running: {' '.join(cmd)}")
  subprocess.run(cmd, check=True, **kwargs)
  print("✓ Done.")

def main():
  os.makedirs(DBT_LOG_PATH, exist_ok=True)
  os.makedirs(DBT_TARGET_PATH, exist_ok=True)

  run(["python", "-u", INGESTION_ENTRYPOINT])

  env = os.environ.copy()
  env["DBT_PROFILES_DIR"] = DBT_PROFILES_DIR
  env["DBT_LOG_PATH"]     = DBT_LOG_PATH
  env["DBT_TARGET_PATH"]  = DBT_TARGET_PATH

  run(["dbt", "deps"], cwd=DBT_PROJECT_DIR, env=env)
  run(["dbt", "run", "--select", "silver", "--threads", "4", "--target", DBT_TARGET],
      cwd=DBT_PROJECT_DIR, env=env)
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
