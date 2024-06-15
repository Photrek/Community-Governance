import cesdb

import streamlit as st
from typing import List


con = cesdb.get_db_connection()

def round_selector(index: int = None):
    rounds_raw = con.sql("SELECT id, name FROM stg_pp_rounds").fetchall()
    rounds = [(row[0], row[1]) for row in rounds_raw]

    option = st.selectbox(
        "Which funding round do you want to evaluate?", 
        rounds,
        format_func=lambda x: x[1],
        index=index,
        placeholder="Select funding round...",
    )

    if not option:
        st.stop()

    st.write(f"You selected: {option[1]}")

    return option

def proposal_selector():
    proposals_raw = con.sql("SELECT id, title FROM proposals").fetchall()
    proposals = [(row[0], f"{row[0]} {row[1]}") for row in proposals_raw]

    option = st.selectbox(
        "Which proposal do you want to evaluate?", 
        proposals,
        format_func=lambda x: x[1],
        index=None,
        placeholder="Select proposal...",
    )

    if option is None:
        option = (None, None)

    st.write(f"You selected: {option[1]}")

    return option

def mandatory_tables_loaded():
    mandatory_tables = [
        # proposal portal tables
        "stg_pp_comment_votes",
        "stg_pp_comments",
        "stg_pp_milestones",
        "stg_pp_pools",
        "stg_pp_proposals",
        "stg_pp_reviews",
        "stg_pp_rounds",
        "stg_pp_rounds_pools",
        "stg_pp_users",

        # voting portal tables
        "stg_vp_agix_balance_snapshot",
        "stg_vp_voting_answers",
        "stg_vp_voting_questions",
        "stg_vp_wallets_collections",

        # analytics tables
        "users",
        "proposals",
        "dfr4_voting_results",
    ]
    loaded_tables = all_tables()

    missing_tables = [table for table in mandatory_tables if table not in loaded_tables]
    if missing_tables:
        print(f"Missing tables: {missing_tables}")

    all_tables_loaded = all(table in loaded_tables for table in mandatory_tables)

    return all_tables_loaded

def all_tables():
    all_tables = con.execute("SHOW ALL TABLES;").fetchall()
    return [table[2] for table in all_tables]

def table_exists(table_name: str):
    return table_name in all_tables()

def tables_exists(table_names: List[str]):
    return all(table_exists(table_name) for table_name in table_names)

def hide_sidebar(hide: bool = True):
    if hide:
        st.markdown("""
        <style>
            section[data-testid="stSidebar"][aria-expanded="true"]{
                display: none;
            }
        </style>
        """, unsafe_allow_html=True)