import cesdb
import utils
import models
import deep_funding_api

import streamlit as st
from typing import Callable


con = cesdb.get_db_connection()

"""
# Data Management
Here you can reset the database and re-load the voting portal data.
"""

# Examples to checkout:
# * https://github.com/mikekenneth/streamlit_duckdb/blob/main/home.py
# * https://github.com/mehd-io/duckdb-dataviz-demo/blob/main/streamlit-demo/app.py
def __progress_updater(progress_text: str) -> Callable[[int, int], None]:
    progress_bar = st.progress(0, text=progress_text)
    return lambda page, total_pages: progress_bar.progress(page / total_pages, text=progress_text)
    
if st.button("Load voting portal data"):
    
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

    """
    Data successfully loaded
    """

if st.button("Hard reset the database", type="primary"):
    con.execute("USE demo;")
    con.execute("DROP SCHEMA db CASCADE;")
    con.execute("CREATE SCHEMA IF NOT EXISTS db;")
    con.execute("USE db;")
    """
    Database successfully reset
    """

def manual_csv_upload(file_name: str, model_name: str, expected_columns: list = []):
    raw_file = st.file_uploader(f"Provide the `{file_name}` containing the columns `{expected_columns}`:", accept_multiple_files=False)
    if raw_file is not None:
        # verify if the csv file contains all the expected columns
        header = raw_file.getvalue().decode().splitlines()[0]
        if not all(column in header for column in expected_columns):
            st.error("CSV file does not contain all the expected columns")
            st.stop()

        with open(f"data/{model_name}.csv", "wb") as f:
            f.write(raw_file.getvalue())
        models.load(con, f'models/silver_{model_name}.sql')

        f"""
        {model_name} successfully loaded
        """

"## Voting Data (excel file)"
def manual_voting_xlsx_upload():
    raw_file = st.file_uploader("Provide the voting data excel file:", accept_multiple_files=False)
    if raw_file is not None:

        with open("data/voting.xlsx", "wb") as f:
            f.write(raw_file.getvalue())

        # enable excel import
        con.execute("INSTALL spatial;")
        con.execute("LOAD spatial;")

        models.load(con, 'models/bronze_answers.sql')
        models.load(con, 'models/bronze_collections.sql')
        models.load(con, 'models/bronze_collection_balances.sql')
        models.load(con, 'models/bronze_questions.sql')

        """
        Voting data successfully loaded
        """


manual_voting_xlsx_upload()

# "## Proposal Rating Data"
# manual_csv_upload(file_name="answers.csv", model_name="ratings", expected_columns=["collection_id", "question_id", "answer", "total_balance"])

# "## Wallet Linking Data"
# manual_csv_upload(file_name="wallet-links.csv", model_name="wallet_links", expected_columns=["address", "collection_id", "balance"])

if not utils.mandatory_tables_loaded():
    utils.hide_sidebar(True)
    st.stop()
else:
    utils.hide_sidebar(False)

if st.button("Go to CES main page"):
    st.switch_page("App.py")
    
"""
# Raw Data
Here you can explore the raw data in the database.
"""


users = con.sql("SELECT * FROM silver_users").df()
"### Users"
users

option = utils.round_selector()
round_id = option[0]

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