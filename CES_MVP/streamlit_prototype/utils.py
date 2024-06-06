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