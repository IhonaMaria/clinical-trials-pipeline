

select distinct
  p.nct_id,
  nullif(trim(x), '') as condition
from "clinical_trials"."bronze"."raw_trials" p,
lateral regexp_split_to_table(p.conditions, '\s*[;,]\s*') as x
where p.conditions is not null and p.conditions <> ''
  and nullif(trim(x), '') is not null