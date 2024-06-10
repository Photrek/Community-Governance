import duckdb

import altair as alt
import streamlit as st


"""
Altair VegaLite Example
"""

@st.cache_resource
def get_db_connection() -> duckdb.DuckDBPyConnection:
    print("get_db_connection")
    con = duckdb.connect(database='demo.db')

    if 'db_connection' not in st.session_state:
        st.session_state['db_connection'] = con
    return con



con = get_db_connection()


users_df = con.sql("SELECT user_id, balance, (ROW_NUMBER() OVER (ORDER BY user_id) * 10) AS pos_x, 100 as pos_y FROM stg_pp_user").df()

users_c = (
   alt.Chart(users_df)
   .mark_circle()
   .encode(x="pos_x", y="pos_y", size="balance", tooltip=["user_id", "balance"])
)

proposals_df = con.sql("SELECT proposal_id, title, ((ROW_NUMBER() OVER (ORDER BY proposal_id)) * 15) AS pos_x, 0 as pos_y FROM stg_pp_proposal").df()

proposals_c = (
   alt.Chart(proposals_df)
   .mark_circle()
   .encode(x="pos_x", y="pos_y", tooltip=["proposal_id", "title"])
)

st.altair_chart((users_c + proposals_c), use_container_width=True)

