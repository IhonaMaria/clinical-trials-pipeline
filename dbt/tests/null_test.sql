{{ config(
    tags=['data_quality', 'not_null'],
    severity='error' -- If test fails, dbt stops the run instead of just warning
) }}

select *
from {{ ref('slv_interventions') }}
where nct_id is null