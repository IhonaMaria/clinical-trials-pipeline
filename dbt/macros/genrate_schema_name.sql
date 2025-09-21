-- Decides which SCHEMA dbt writes this model to.
-- No schema set on the model? -> use target.schema
-- Model sets config(schema='gold')? -> use 'gold'

{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name }}
    {%- endif -%}
{%- endmacro %}
