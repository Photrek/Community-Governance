import cesdb

import streamlit as st


con = cesdb.get_db_connection()

def round_selector():
    rounds_raw = con.sql("SELECT id, name FROM silver_rounds").fetchall()
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

    f"You selected: {option[1]}"

    return option

def mandatory_tables_loaded():
    mandatory_tables = [
        "silver_comment_votes",
        "silver_proposals",
        "silver_rounds_pools",
        "silver_comments",
        "silver_users",
        "silver_milestones",
        "silver_reviews",
        "silver_pools",
        "silver_rounds",

        # expect excel import
        "bronze_questions",
        # "silver_wallet_links",
        # "silver_ratings",
    ]
    loaded_tables = con.execute("SHOW ALL TABLES;").fetchall()
    loaded_tables = [table[2] for table in loaded_tables]

    missing_tables = [table for table in mandatory_tables if table not in loaded_tables]
    if missing_tables:
        print(f"Missing tables: {missing_tables}")

    all_tables_loaded = all(table in loaded_tables for table in mandatory_tables)

    return all_tables_loaded

def hide_sidebar(hide: bool = True):
    if hide:
        st.markdown("""
        <style>
            section[data-testid="stSidebar"][aria-expanded="true"]{
                display: none;
            }
        </style>
        """, unsafe_allow_html=True)