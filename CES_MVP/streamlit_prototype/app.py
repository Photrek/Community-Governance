import cesdb
import utils
import models
import deep_funding_api

import streamlit as st
from typing import Callable


#
# Helper functions
#

con = cesdb.get_db_connection()

# Examples to checkout:
# * https://github.com/mikekenneth/streamlit_duckdb/blob/main/home.py
# * https://github.com/mehd-io/duckdb-dataviz-demo/blob/main/streamlit-demo/app.py
def __progress_updater(progress_text: str) -> Callable[[int, int], None]:
    progress_bar = st.progress(0, text=progress_text)
    return lambda page, total_pages: progress_bar.progress(page / total_pages, text=progress_text)
    
def manual_voting_xlsx_upload():
    raw_file = st.file_uploader("Provide the voting data excel file:", accept_multiple_files=False)
    if raw_file is not None:

        with open("data/voting.xlsx", "wb") as f:
            f.write(raw_file.getvalue())

        # enable excel import
        con.execute("INSTALL spatial;")
        con.execute("LOAD spatial;")

        models.load(con, 'models/staging/voting_portal/stg_vp_ratings.sql')
        models.load(con, 'models/staging/voting_portal/stg_vp_collections.sql')
        models.load(con, 'models/staging/voting_portal/stg_vp_collection_balances.sql')
        models.load(con, 'models/staging/voting_portal/stg_vp_questions.sql')

        """
        🎉 Voting data successfully loaded
        """

# Page content starts here

"""
# Data Management
Load the data into the local database and prepare it for analysis.

## Voting Portal - Data (excel file)
Make sure the excel file provides the following sheets (case-sensitive):
- Answers
- Collections
- Collections Balances
- Questions
"""

manual_voting_xlsx_upload()

"## Proposal Portal - Data (API)"

if st.button("Fetch from API"):
    
    progress_text = "Fetching general vorting portal data. Please wait."
    progress_bar = st.progress(0, text=progress_text)

    deep_funding_api.load_rounds_and_pools_connection()
    progress_bar.progress(0.5, text=progress_text)

    deep_funding_api.load_pools()
    progress_bar.progress(1.0, text=progress_text)

    
    deep_funding_api.load_users(progress_updater=__progress_updater("Fetching users from voting portal. Please wait."))

    deep_funding_api.load_comments(progress_updater=__progress_updater("Fetching comments from voting portal. Please wait."))

    deep_funding_api.load_proposals(progress_updater=__progress_updater("Fetching proposals from voting portal. Please wait."))
    
    deep_funding_api.load_milestones(progress_updater=__progress_updater("Fetching milestones from voting portal. Please wait."))
    
    deep_funding_api.load_reviews(progress_updater=__progress_updater("Fetching reviews from voting portal. Please wait."))
    
    deep_funding_api.load_comment_votes(progress_updater=__progress_updater("Fetching comment votes from voting portal. Please wait."))

    if utils.table_exists("stg_vp_ratings"):
        models.marts_transformations(con, 'models')

    """
    Data successfully loaded
    """

"## Danger Zone"

if st.button("Reset local database", type="primary"):
    con.execute("USE demo;")
    con.execute("DROP SCHEMA db CASCADE;")
    con.execute("CREATE SCHEMA IF NOT EXISTS db;")
    con.execute("USE db;")
    """
    Database successfully reset
    """

if not utils.mandatory_tables_loaded():
    utils.hide_sidebar(True)
    st.stop()
else:
    utils.hide_sidebar(False)