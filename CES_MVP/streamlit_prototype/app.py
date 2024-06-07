
import cesdb
import utils

import streamlit as st
import gravis as gv
import networkx as nx

import streamlit.components.v1 as components

# Examples to checkout:
# * https://github.com/mikekenneth/streamlit_duckdb/blob/main/home.py
# * https://github.com/mehd-io/duckdb-dataviz-demo/blob/main/streamlit-demo/app.py


"""
# Community Engagement Score

1. Load the portal data
2. Load the voting data
"""

con = cesdb.get_db_connection()

if utils.mandatory_tables_loaded():
    utils.hide_sidebar(False)
else:
    utils.hide_sidebar(True)
    st.switch_page("pages/1_🗂️_Input_Data.py")
    
# TODO:
# 1. once everyhing is loaded, perform gold transformations
# 2. visualize the data in the network graph

st.stop()

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

TODO: try out pyvis if it's faster: https://pyvis.readthedocs.io/en/latest/tutorial.html#getting-started
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

edges_query = """
SELECT
    r.user_id,
    r.proposal_id,
    e.entropy,
FROM
    silver_rating as r
JOIN gold_entropy as e ON
    r.user_id = e.user_id,
"""

ratings = con.sql(edges_query).fetchall()
n_half = len(ratings) // 2
for i, row in enumerate(ratings):
    user_id = f"user_{row[0]}"
    proposal_id = f"proposal_{row[1]}"
    entropy = row[2] * 5

    g.add_edge(user_id, proposal_id, color='green', size=entropy)


fig = gv.d3(g, show_node_label=True, node_drag_fix=True, node_hover_neighborhood=True)
components.html(fig.to_html(), height=600)

"""
Voting Entropy
"""

voting_entropy = con.sql("SELECT * FROM gold_entropy").df()
voting_entropy

st.bar_chart(data=voting_entropy, x='user_id', y='entropy')


voting_entropy = con.sql("""
with max_votes as (
    select
        count(*) as total_users
    from
        silver_user
)

select 
    r.proposal_id,
    (
        SUM(CASE WHEN r.grade <> 'skip' THEN r.grade::int * e.entropy END)
        / (LOG2(11) * (SELECT total_users FROM max_votes) )
    ) total_entropy,
from
    silver_rating as r
join gold_entropy as e on
    r.user_id = e.user_id
group by
    1
order by total_entropy desc
""").df()
voting_entropy

st.bar_chart(data=voting_entropy, x='proposal_id', y='total_entropy')

