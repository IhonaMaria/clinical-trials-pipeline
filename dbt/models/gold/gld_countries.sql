{{
  config(
    materialized = 'table'
  )
}}

select
  tc.nct_id,
  tc.country,
  cc.latitude,
  cc.longitude
from {{ ref('slv_countries') }} tc
left join {{ ref('country_codes') }} cc
  on lower(cc.country) = lower(tc.country)
