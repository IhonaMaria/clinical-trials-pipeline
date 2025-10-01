{{ config(tags=['data_quality','not_null'], severity='error') }}

select *
from {{ ref('slv_interventions') }}
where nct_id is null
