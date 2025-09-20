
  
    

  create  table "clinical_trials"."silver"."slv_countries__dbt_tmp"
  
  
    as
  
  (
    

select distinct
  p.nct_id,
  nullif(trim(x), '') as country
from "clinical_trials"."bronze"."raw_trials" p,
lateral regexp_split_to_table(p.countries, '\s*[;,]\s*') as x
where p.countries is not null and p.countries <> ''
  and nullif(trim(x), '') is not null
  );
  