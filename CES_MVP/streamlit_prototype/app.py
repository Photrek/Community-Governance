import duckdb
import models
import time

import streamlit as st
import gravis as gv
import networkx as nx
import streamlit.components.v1 as components

# Examples to checkout:
# * https://github.com/mikekenneth/streamlit_duckdb/blob/main/home.py
# * https://github.com/mehd-io/duckdb-dataviz-demo/blob/main/streamlit-demo/app.py


"""
# Community Engagement Score Prototype
"""

@st.cache_resource
def get_db_connection() -> duckdb.DuckDBPyConnection:
    print("get_db_connection")
    con = duckdb.connect(database='demo.db')
    models.load_all(con, 'models')

    if 'db_connection' not in st.session_state:
        st.session_state['db_connection'] = con
    return con


uploaded_files = st.file_uploader("Choose a CSV file", accept_multiple_files=True)
# for uploaded_file in uploaded_files:
    # TODO: Load the CSV file into the database
    # TODO: once all files are present, hide the file uploader and show the data
    # st.write("filename:", uploaded_file.name)
    
if uploaded_files:
    con = get_db_connection()


    """
    ## Input Data
    """
    proposals = con.sql("SELECT * FROM silver_proposal").df()
    "### Proposals"
    proposals

    ratings = con.sql("SELECT * FROM silver_rating").df()
    "### Ratings"
    ratings 

    users = con.sql("SELECT * FROM silver_user").df()
    "### Users"
    users


    """
    ## Vote results
    """
    option = st.selectbox(
        'Vote weight algorithm:',
        ('one_user_one_vote_weighted_sqrt', 'one_user_one_vote'))

    st.write('You selected:', option)

    algorithm = ""
    if option == 'one_user_one_vote_weighted_sqrt':
        algorithm = """
            -- remove skipped votes
            SUM(CASE WHEN r.grade <> 'skip' THEN sqrt(r.total_balance) * CAST(r.grade AS INTEGER) END) / 
            NULLIF(SUM(CASE WHEN r.grade <> 'skip' THEN sqrt(r.total_balance) END), 0),
        """
    else:
        algorithm = """
            -- remove skipped votes
            SUM(CASE WHEN r.grade <> 'skip' THEN CAST(r.grade AS INTEGER) END) / 
            NULLIF(COUNT(CASE WHEN r.grade <> 'skip' THEN 1 END), 0), 
        """

    query = f"""
    SELECT
        p.proposal_id,
        p.title,
        COUNT(CASE WHEN r.grade <> 'skip' THEN 1 END) AS num_votes,

        -- need the skipped answers to calculate % of people that voted
        (COUNT(CASE WHEN r.grade <> 'skip' THEN 1 END) * 100.0) / COUNT(r.*) AS percent_voted,

        -- average grade
        NULLIF(
            {algorithm}
        0) AS avg_grade
    FROM 
        silver_proposal AS p
    LEFT JOIN 
        silver_rating AS r
    ON p.proposal_id = r.proposal_id
    GROUP BY 
        p.proposal_id, 
        p.title
    """

    vote_results = con.sql(query).df()
    vote_results

    st.bar_chart(data=vote_results, x='proposal_id', y='avg_grade')


    """
    Network Analysis
    """
    g = nx.DiGraph()

    users = con.sql("SELECT user_id FROM silver_user").fetchall()
    n_half = len(users) // 2
    for i, row in enumerate(users):
        id = f"user_{row[0]}"
        x = (i - n_half) * 40
        y = 100

        g.add_node(id, x=x, y=y, color='blue')

    proposals = con.sql("SELECT proposal_id FROM silver_proposal").fetchall()
    n_half = len(proposals) // 2
    for i, row in enumerate(proposals):
        id = f"proposal_{row[0]}"
        x = (i - n_half) * 40
        y = -100

        g.add_node(id, x=x, y=y, color='red')

    ratings = con.sql("SELECT user_id, proposal_id FROM silver_rating").fetchall()
    n_half = len(ratings) // 2
    for i, row in enumerate(ratings):
        user_id = f"user_{row[0]}"
        proposal_id = f"proposal_{row[1]}"

        g.add_edge(user_id, proposal_id, color='green')


    fig = gv.d3(g, show_node_label=True, node_drag_fix=True, node_hover_neighborhood=True)
    components.html(fig.to_html(), height=600)
