
  
    

  create  table "clinical_trials"."gold"."gld-countries__dbt_tmp"
  
  
    as
  
  (
    

select
  tc.nct_id,
  tc.country,
  cc.latitude,
  cc.longitude
from "clinical_trials"."silver"."slv-countries" tc
left join "clinical_trials"."silver"."country_codes" cc
  on lower(cc.country) = lower(tc.country)
  );
  