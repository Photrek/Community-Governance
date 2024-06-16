import cesdb
import utils
import models
import deep_funding_api

import streamlit as st
from typing import Callable

import streamlit as st

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
    
def manual_voting_xlsx_upload() -> bool:
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
        return True
    else:
        return False
    
def manual_voting_csv_upload(file_name: str) -> bool:
    if utils.table_exists(f"stg_vp_{file_name}"):
        return True
    # Allow user to upload a single CSV file
    raw_file = st.file_uploader(f"Provide the {file_name} csv file:", accept_multiple_files=False)
    if raw_file is not None:
            
            # TODO: Check if the file has the expected columns
            
            with open(f"data/{file_name}.csv", "wb") as f:
                f.write(raw_file.getvalue())
    
            models.load(con, f'models/dfr4/staging/voting_portal/stg_vp_{file_name}.sql')
    
            f"""
            🎉 {file_name} successfully loaded
            """
            st.rerun()
            return True

# Page content starts here

"""
# Data Management
Load the data into the local database and prepare it for analysis.

## Voting Portal - Data
"""

voting_portal_answers_loaded = manual_voting_csv_upload("voting_answers")
voting_portal_questions_loaded = manual_voting_csv_upload("voting_questions")
voting_portal_wallets_collections_loaded = manual_voting_csv_upload("wallets_collections")
voting_portal_agix_balance_snapshot_loaded = manual_voting_csv_upload("agix_balance_snapshot")

# voting_portal_loaded = manual_voting_xlsx_upload()

if utils.tables_exists([
    "stg_vp_agix_balance_snapshot",
    "stg_vp_voting_answers",
    "stg_vp_voting_questions",
    "stg_vp_wallets_collections",
]):
    """
    🎉 Voting data successfully loaded

    """

    "## Proposal Portal - Data (API)"

    do_refetch_data = st.checkbox("Refetch from API", value=True)
    fake_user_collection_ids = st.checkbox("Fake user collection ids", value=False)

    if st.button("Fetch from API"):
        
        progress_text = "Fetching general vorting portal data. Please wait."
        progress_bar = st.progress(0, text=progress_text)

        deep_funding_api.load_rounds_and_pools_connection(refetch=do_refetch_data)
        progress_bar.progress(0.5, text=progress_text)

        deep_funding_api.load_pools(refetch=do_refetch_data)
        progress_bar.progress(1.0, text=progress_text)

        
        deep_funding_api.load_users(
            refetch=do_refetch_data,
            progress_updater=__progress_updater("Fetching users from voting portal. Please wait.")
        )

        deep_funding_api.load_comments(
            refetch=do_refetch_data,
            progress_updater=__progress_updater("Fetching comments from voting portal. Please wait.")
        )

        deep_funding_api.load_proposals(
            refetch=do_refetch_data,
            progress_updater=__progress_updater("Fetching proposals from voting portal. Please wait.")
        )
        
        deep_funding_api.load_milestones(
            refetch=do_refetch_data,
            progress_updater=__progress_updater("Fetching milestones from voting portal. Please wait.")
        )
        
        deep_funding_api.load_reviews(
            refetch=do_refetch_data,
            progress_updater=__progress_updater("Fetching reviews from voting portal. Please wait.")
        )
        
        deep_funding_api.load_comment_votes(
            refetch=do_refetch_data,
            progress_updater=__progress_updater("Fetching comment votes from voting portal. Please wait.")
        )



        ## prepare data
        models.load(con, 'models/intermediate/int_collection_balances.sql')
        models.load(con, 'models/intermediate/int_proposal_mapping.sql')
        models.load(con, 'models/intermediate/int_ratings.sql')

        models.load(con, 'models/marts/proposals.sql')
        if fake_user_collection_ids:
            models.load(con, 'models/marts/users_fake.sql', model_name='users')
        else:
            models.load(con, 'models/marts/users.sql')

        ## int_engagement_score
        models.load(con, 'models/dfr4/intermediate/int_comment_counts.sql')
        models.load(con, 'models/dfr4/intermediate/int_comment_votes.sql')
        models.load(con, 'models/dfr4/intermediate/int_engagement_score.sql')

        ## int_reputation_weight
        models.load(con, 'models/dfr4/intermediate/int_total_voting_weight.sql')
        models.load(con, 'models/dfr4/intermediate/int_min_max_engagement_score_per_proposal.sql')
        models.load(con, 'models/dfr4/intermediate/int_reputation_weight.sql')

        ## Marts
        models.load(con, 'models/dfr4/marts/voting_weights.sql')
        models.load(con, 'models/dfr4/intermediate/int_votes_per_proposal.sql')
        models.load(con, 'models/dfr4/marts/dfr4_voting_results.sql')


        # Entropy
        models.load(con, 'models/marts/entropy.sql')
        #     models.load(con, 'models/marts/vote_results.sql')

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
    st.rerun()

if not utils.mandatory_tables_loaded():
    utils.hide_sidebar(True)
else:
    utils.hide_sidebar(False)