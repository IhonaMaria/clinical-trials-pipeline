
  
    

  create  table "clinical_trials"."silver"."slv_processed_trials__dbt_tmp"
  
  
    as
  
  (
    

with src as (
  select
    nct_id,
    brief_title,
    study_type,
    case
      when coalesce(upper(study_type), '') = 'OBSERVATIONAL' then 'NOT APPLICABLE'
      when phase is null then null
      else upper(phase)
    end as phase,
    overall_status,
    start_date      as start_date_raw,
    completion_date as completion_date_raw
  from "clinical_trials"."bronze"."raw_trials"
),

-- 1) Homogenize placeholders -> NULL
nulls as (
  select
    nct_id,
    nullif(trim(brief_title),      '')              as brief_title,
    nullif(trim(study_type),       '')              as study_type,
    nullif(trim(phase),            '')              as phase,
    nullif(trim(overall_status),   '')              as status,
    nullif(trim(start_date_raw),       '')          as start_date_raw,
    nullif(trim(completion_date_raw),  '')          as completion_date_raw
  from src
),

-- Treat common placeholders (‘NA’, ‘N/A’, ‘UNKNOWN’, ‘NULL’ the *string*) as NULL
placeholders as (
  select
    nct_id,
    case when upper(brief_title)    in ('NA','N/A','UNKNOWN','NULL') then null else brief_title end    as brief_title,
    case when upper(study_type)     in ('NA','N/A','UNKNOWN','NULL') then null else study_type  end    as study_type,
    case when upper(phase)       in ('NA','N/A','UNKNOWN','NULL') then null else phase    end    as phase,
    case when upper(status)      in ('NA','N/A','UNKNOWN','NULL') then null else status   end    as status,
    case when upper(start_date_raw)     in ('NA','N/A','UNKNOWN','NULL') then null else start_date_raw  end    as start_date_raw,
    case when upper(completion_date_raw)in ('NA','N/A','UNKNOWN','NULL') then null else completion_date_raw end as completion_date_raw
  from nulls
),

-- 2) Parse partial dates (YYYY, YYYY-MM, YYYY-MM-DD) -> DATE
dates as (
  select
    nct_id,
    brief_title,
    study_type,
    status,
    phase,

    case
      when start_date_raw ~ '^\d{4}-\d{2}-\d{2}$' then to_date(start_date_raw,'YYYY-MM-DD')
      when start_date_raw ~ '^\d{4}-\d{2}$'       then to_date(start_date_raw||'-01','YYYY-MM-DD')
      when start_date_raw ~ '^\d{4}$'             then to_date(start_date_raw||'-01-01','YYYY-MM-DD')
      else null
    end as start_date,

    case
      when completion_date_raw ~ '^\d{4}-\d{2}-\d{2}$' then to_date(completion_date_raw,'YYYY-MM-DD')
      when completion_date_raw ~ '^\d{4}-\d{2}$'       then to_date(completion_date_raw||'-01','YYYY-MM-DD')
      when completion_date_raw ~ '^\d{4}$'             then to_date(completion_date_raw||'-01-01','YYYY-MM-DD')
      else null
    end as completion_date
  from placeholders
)

select 
    nct_id,
    brief_title,
    study_type,
    status,
    phase,
    start_date,
    completion_date
from dates
  );
  