import cesdb

import streamlit as st


con = cesdb.get_db_connection()

def round_selector():
    rounds_raw = con.sql("SELECT id, name FROM stg_pp_rounds").fetchall()
    rounds = [(row[0], row[1]) for row in rounds_raw]

    option = st.selectbox(
    "Which funding round do you want to evaluate?", 
    rounds,
    format_func=lambda x: x[1],
    index=None,
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
        "stg_pp_comment_votes",
        "stg_pp_proposals",
        "stg_pp_rounds_pools",
        "stg_pp_comments",
        "stg_pp_users",
        "stg_pp_milestones",
        "stg_pp_reviews",
        "stg_pp_pools",
        "stg_pp_rounds",

        # expect excel import
        "stg_vp_questions",
        # "stg_pp_wallet_links",
        # "stg_vp_ratings",
    ]
    loaded_tables = con.execute("SHOW ALL TABLES;").fetchall()
    loaded_tables = [table[2] for table in loaded_tables]

    missing_tables = [table for table in mandatory_tables if table not in loaded_tables]
    if missing_tables:
        print(f"Missing tables: {missing_tables}")

    all_tables_loaded = all(table in loaded_tables for table in mandatory_tables)

    return all_tables_loaded

def all_tables():
    all_tables = con.execute("SHOW ALL TABLES;").fetchall()
    return [table[2] for table in all_tables]

def table_exists(table_name):
    return table_name in all_tables()

def hide_sidebar(hide: bool = True):
    if hide:
        st.markdown("""
        <style>
            section[data-testid="stSidebar"][aria-expanded="true"]{
                display: none;
            }
        </style>
        """, unsafe_allow_html=True)