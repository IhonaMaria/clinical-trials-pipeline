l{{ config(tags=['data_quality', 'not_null'], severity='error') }}

select *
from {{ ref('silver__studies') }}
where nct_id is null
