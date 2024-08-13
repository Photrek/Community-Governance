{% macro export_csv(table_name) %}
    {% set file_path = '../exports/' ~ table_name ~ '.csv' %}
    
    {% set query %}
        COPY (SELECT * FROM {{ ref(table_name) }}) TO '{{ file_path }}' WITH (FORMAT CSV, HEADER TRUE);
    {% endset %}
    
    {% do run_query(query) %}
{% endmacro %}