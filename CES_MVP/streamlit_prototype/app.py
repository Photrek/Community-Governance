import duckdb
import models

import streamlit as st
import gravis as gv
import networkx as nx
import streamlit.components.v1 as components

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
vote_results = con.sql("SELECT * FROM gold_vote_results").df()
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
    y = 400

    g.add_node(id, x=x, y=y, color='blue')

proposals = con.sql("SELECT proposal_id FROM silver_proposal").fetchall()
n_half = len(proposals) // 2
for i, row in enumerate(proposals):
    id = f"proposal_{row[0]}"
    x = (i - n_half) * 40
    y = 0

    g.add_node(id, x=x, y=y, color='red')

ratings = con.sql("SELECT user_id, proposal_id FROM silver_rating").fetchall()
n_half = len(ratings) // 2
for i, row in enumerate(ratings):
    user_id = f"user_{row[0]}"
    proposal_id = f"proposal_{row[1]}"

    g.add_edge(user_id, proposal_id, color='green')


fig = gv.d3(g, show_node_label=False, node_drag_fix=True, node_hover_neighborhood=True)
components.html(fig.to_html(), height=600)
