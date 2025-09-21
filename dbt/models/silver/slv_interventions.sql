{{
  config(
    materialized = 'table'
  )
}}

-- Goal: Explode the comma/semicolon separated interventions for each ID.
select distinct
  p.nct_id,
  nullif(trim(x), '') as intervention
from {{ source('bronze', 'raw_trials') }} p,
lateral regexp_split_to_table(p.interventions, '\s*[;,]\s*') as x
where p.interventions is not null and p.interventions <> ''
  and nullif(trim(x), '') is not null

