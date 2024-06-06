import cesdb
import utils

import streamlit as st

# Examples to checkout:
# * https://github.com/mikekenneth/streamlit_duckdb/blob/main/home.py
# * https://github.com/mehd-io/duckdb-dataviz-demo/blob/main/streamlit-demo/app.py


"""
# Input Data
"""

con = cesdb.get_db_connection()

option = utils.round_selector()
round_id = option[0]

"""
## Input Data
"""

users = con.sql("SELECT * FROM silver_users").df()
"### Users"
users

col1, col2 = st.columns(2)

with col1:
    proposals = con.sql(f"SELECT * FROM silver_proposals where round_id = {round_id}").df()
    "### Proposals"
    proposals

with col2:
    comments = con.sql(f"""
                       SELECT * 
                       FROM silver_comments
                       WHERE proposal_id IN (
                           SELECT id
                           FROM silver_proposals
                           WHERE round_id = {round_id}
                       )
                       """).df()
    "### Comments"
    comments