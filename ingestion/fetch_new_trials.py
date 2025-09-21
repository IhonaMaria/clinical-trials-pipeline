# 1. Pulls recent clinical trials from the API
# 2. Flattens the fields 
# 3. Saves the fields into Postgres in a bronze table called raw_trials

import requests
import psycopg2

# API endpoint and DB connection settings
BASE_URL = "https://clinicaltrials.gov/api/v2/studies"
DB_CONFIG = {
    "dbname": "clinical_trials",
    "user": "user",
    "password": "password",
    "host": "postgres",
    "port": 5432
}

def fetch_latest_trials(limit=1000):
    # Ask the API for 100 studies per page and total count
    params = {
        "pageSize": 100,        
        "countTotal": "true"
    }

    studies = []
    next_token = None
    total_fetched = 0

    # Keep paging until we reach the limit or run out of pages
    while total_fetched < limit:
        if next_token:
            params["pageToken"] = next_token
        resp = requests.get(BASE_URL, params=params, timeout=30) # Call the API 
        print("Requesting:", resp.url)
        
        # Raise a detailed error if HTTP status is not OK
        try:
            resp.raise_for_status()
        except requests.HTTPError:
            print("API error body:", resp.text)
            raise

        data = resp.json()
        items = data.get("studies", [])
        if not items:
            break
        
        # Extract/flatten the fields we need from each study
        for s in items:
            ps = s.get("protocolSection", {})
            ident = ps.get("identificationModule", {})
            status = ps.get("statusModule", {})
            design = ps.get("designModule", {})
            conds = ps.get("conditionsModule", {}).get("conditions", [])
            intervs = ps.get("armsInterventionsModule", {}).get("interventions", [])
            locs = ps.get("contactsLocationsModule", {}).get("locations", [])

            studies.append({
                "nct_id": ident.get("nctId"),
                "brief_title": ident.get("briefTitle"),
                "study_type": design.get("studyType"),
                "phase": (design.get("phases") or [None])[0],
                "overall_status": status.get("overallStatus"),
                "start_date": (status.get("startDateStruct") or {}).get("date"),
                "completion_date": (status.get("completionDateStruct") or {}).get("date"),
                "conditions": "; ".join(conds) if conds else None,
                "interventions": "; ".join([i.get("name","") for i in intervs]) if intervs else None,
                "countries": "; ".join([loc.get("country","") for loc in locs]) if locs else None
            })
            total_fetched += 1
            if total_fetched >= limit:
                break

        next_token = data.get("nextPageToken")
        if not next_token:
            break

    studies.sort(key=lambda r: (r["start_date"] is None, r["start_date"]), reverse=True) # Sort studies by start date
    return [
        (r["nct_id"], r["brief_title"], r["study_type"], r["phase"], r["overall_status"],
         r["start_date"], r["completion_date"], r["conditions"], r["interventions"], r["countries"])
        for r in studies
    ]
    
 # Connect and create bronze schema/table if needed

def insert_into_postgres(studies):
    if not studies:
        print("No new studies to insert.")
        return
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        CREATE SCHEMA IF NOT EXISTS bronze;
        CREATE TABLE IF NOT EXISTS bronze.raw_trials (
            nct_id TEXT PRIMARY KEY,
            brief_title TEXT,
            study_type TEXT,
            phase TEXT,
            overall_status TEXT,
            start_date TEXT,
            completion_date TEXT,
            conditions TEXT,
            interventions TEXT,
            countries TEXT
        );
    """)
    
    # Insert rows and ignore duplicates for nct_id
    cur.executemany("""
        INSERT INTO bronze.raw_trials (
            nct_id, brief_title, study_type, phase, overall_status,
            start_date, completion_date, conditions, interventions, countries
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (nct_id) DO NOTHING;
    """, studies)
    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted {len(studies)} records into bronze.raw_trials")

if __name__ == "__main__":
    print("Fetching latest trials ...")
    trials = fetch_latest_trials(limit=1000)
    insert_into_postgres(trials)
