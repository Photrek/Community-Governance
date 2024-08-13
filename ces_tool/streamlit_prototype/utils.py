import cesdb

import streamlit as st
from typing import List
import pandas as pd
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)


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

def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """

    unique_key = hash(tuple(df.columns))

    # hash all column names to generate unique key
    # to avoid conflicts with other dataframes
    modify = st.checkbox(label="Add filters", key=f"{unique_key}_filter")

    if not modify:
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            left.write("↳")
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    _min,
                    _max,
                    (_min, _max),
                    step=step,
                    key=f"{unique_key}_{column}",
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].str.contains(user_text_input)]

    return df