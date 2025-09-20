
  
    

  create  table "clinical_trials"."gold"."gld_interventions__dbt_tmp"
  
  
    as
  
  (
    

select *
from "clinical_trials"."silver"."slv_interventions"
  );
  