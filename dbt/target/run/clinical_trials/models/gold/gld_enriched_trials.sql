
  
    

  create  table "clinical_trials"."gold"."gld_enriched_trials__dbt_tmp"
  
  
    as
  
  (
    

SELECT
    nct_id,
    brief_title,
    study_type,
    status,
    phase,
    start_date,
    completion_date,
    case
        when start_date is not null
        and completion_date is not null
        and completion_date >= start_date
        then round(((completion_date - start_date)::numeric / 365.25), 2)
        else null
    end as study_length_years
from "clinical_trials"."silver"."slv_processed_trials"
  );
  