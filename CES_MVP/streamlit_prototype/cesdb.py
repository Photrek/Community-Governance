import duckdb

import streamlit as st


@st.cache_resource
def get_db_connection() -> duckdb.DuckDBPyConnection:
    print("get_db_connection")
    con = duckdb.connect(database='demo.db')
    # models.load_all(con, 'models')
    con.sql("CREATE SCHEMA IF NOT EXISTS db;")
    con.sql("USE db;")

    # if 'db_connection' not in st.session_state:
    #     st.session_state['db_connection'] = con
    return con