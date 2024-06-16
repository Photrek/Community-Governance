import duckdb
import os

import streamlit as st

read_mode = os.getenv('READ_ONLY', 'false') == 'true'

@st.cache_resource
def get_db_connection() -> duckdb.DuckDBPyConnection:

    # if running in Docker container, remove existing database
    if os.path.exists('demo.db') and os.getenv('DOCKER') == 'true':
        print("Removing existing database")
        os.remove('demo.db')

    print("get_db_connection")
    con = duckdb.connect(database='demo.db', read_only=read_mode)
    
    if not read_mode:
        con.sql("CREATE SCHEMA IF NOT EXISTS db;")
        con.sql("USE db;")
        create_function(con, 'levenshtein', levenshtein)
    con.sql("USE db;")


    # if 'db_connection' not in st.session_state:
    #     st.session_state['db_connection'] = con
    return con

def levenshtein(a, b) -> int:
    """
    Calculate the Levenshtein distance between two strings.
    """
    
    if len(a) < len(b):
        return levenshtein(b, a)
    if len(b) == 0:
        return len(a)
    prev_row = range(len(b) + 1)
    for i, c1 in enumerate(a):
        current_row = [i + 1]
        for j, c2 in enumerate(b):
            insertions = prev_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        prev_row = current_row
    return prev_row[-1]

def create_function(con, function_name, function):
    """
    Create a function in DuckDB.
    """
    function_check = f"""SELECT DISTINCT  function_name
                        FROM duckdb_functions()
                        WHERE lower(function_type) = 'scalar'
                        AND lower(function_name) in ('{function_name}')
                        ORDER BY function_name;"""

    function_check_output = con.query(function_check)
    try:
        if not function_check_output:
            con.create_function(function_name, function)
            print(f"Function '{function_name}' created successfully.")
    except (duckdb.Error, ValueError) as error:
        raise ValueError(
            f"Failed to create function '{function_name}': {str(error)}"
        ) from error