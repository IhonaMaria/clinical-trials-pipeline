
  
    

  create  table "clinical_trials"."gold"."gld_conditions__dbt_tmp"
  
  
    as
  
  (
    

select *
from "clinical_trials"."silver"."slv_conditions"
  );
  