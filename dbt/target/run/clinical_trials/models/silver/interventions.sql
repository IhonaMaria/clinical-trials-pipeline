
  
    

  create  table "clinical_trials"."silver"."interventions__dbt_tmp"
  
  
    as
  
  (
    

select distinct
  p.nct_id,
  nullif(trim(x), '') as intervention
from "clinical_trials"."bronze"."raw_trials" p,
lateral regexp_split_to_table(p.interventions, '\s*[;,]\s*') as x
where p.interventions is not null and p.interventions <> ''
  and nullif(trim(x), '') is not null
  );
  