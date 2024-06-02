import duckdb
import json
import voting
import models

import streamlit as st
import gravis as gv
import networkx as nx
import streamlit.components.v1 as components

# Examples to checkout:
# * https://github.com/mikekenneth/streamlit_duckdb/blob/main/home.py
# * https://github.com/mehd-io/duckdb-dataviz-demo/blob/main/streamlit-demo/app.py


"""
# Community Engagement Score

To evaluate the voting results:

1. Choose which voting results you want to fetch
1. Load the data from the voting results
1. Upload the wallet-linking CSV file
"""

# @st.cache_resource
def get_db_connection() -> duckdb.DuckDBPyConnection:
    print("get_db_connection")
    con = duckdb.connect(database='demo.db')
    # models.load_all(con, 'models')
    con.sql("CREATE SCHEMA IF NOT EXISTS db;")
    con.sql("USE db;")

    # if 'db_connection' not in st.session_state:
    #     st.session_state['db_connection'] = con
    return con


# TODO add check if data is already loaded
# TODO add "hard refresh" button
def fetch_users():
    progress_text = "Fetching users from vorting portal. Please wait."
    progress_bar = st.progress(0, text=progress_text)
    all_users = []
    for page_number, (page_data, total_pages) in enumerate(voting.download_users(), start=1):
        # Update the progress bar
        progress = page_number / total_pages
        progress_bar.progress(progress, text=progress_text)

        all_users.extend(page_data)

    with open('data/users.json', 'w') as f:
        json.dump(all_users, f)
    
    models.load(con, 'models/silver_users.sql')

def fetch_comments():
    progress_text = "Fetching comments from vorting portal. Please wait."
    progress_bar = st.progress(0, text=progress_text)
    all_users = []
    for page_number, (page_data, total_pages) in enumerate(voting.download_comments(), start=1):
        # Update the progress bar
        progress = page_number / total_pages
        progress_bar.progress(progress, text=progress_text)

        all_users.extend(page_data)
    with open('data/comments.json', 'w') as f:
        json.dump(all_users, f)

    models.load(con, 'models/silver_comments.sql')

con = get_db_connection()
# TODO: drop database if exists


def fetch_proposals(con):
    rounds = con.sql("SELECT id FROM silver_rounds").fetchall()
    round_ids = [row[0] for row in rounds]

    progress_text = "Fetching proposals from vorting portal. Please wait."
    progress_bar = st.progress(0, text=progress_text)

    proposals = []
    for idx, round in enumerate(round_ids, start=1):
        response = voting.download_proposals(round_id=round)
        proposals.extend(response)
        progress_bar.progress(idx / len(round_ids), text=progress_text)

    with open('data/proposals.json', 'w') as f:
        json.dump(proposals, f)

    models.load(con, 'models/silver_proposals.sql')

def fetch_milestones(con):
    proposals = con.sql("SELECT id FROM silver_proposals").fetchall()
    proposal_ids = [row[0] for row in proposals]

    progress_text = "Fetching milestones from vorting portal. Please wait."
    progress_bar = st.progress(0, text=progress_text)

    milestones = []
    for idx, proposal in enumerate(proposal_ids, start=1):
        response = voting.download_milestones(proposal_id=proposal)
        milestones.extend(response)
        progress_bar.progress(idx / len(proposal_ids), text=progress_text)

    with open('data/milestones.json', 'w') as f:
        json.dump(milestones, f)

    models.load(con, 'models/silver_milestones.sql')

def fetch_reviews(con):
    proposals = con.sql("SELECT id FROM silver_proposals").fetchall()
    proposal_ids = [row[0] for row in proposals]

    progress_text = "Fetching reviews from vorting portal. Please wait."
    progress_bar = st.progress(0, text=progress_text)

    reviews = []
    for idx, proposal in enumerate(proposal_ids, start=1):
        response = voting.download_reviews(proposal_id=proposal)
        reviews.extend(response)
        progress_bar.progress(idx / len(proposal_ids), text=progress_text)

    with open('data/reviews.json', 'w') as f:
        json.dump(reviews, f)

    models.load(con, 'models/silver_reviews.sql')

def fetch_comment_votes(con):
    comments = con.sql("SELECT * FROM silver_comments WHERE comment_votes > 0").fetchall()
    comments_ids = [row[0] for row in comments]

    progress_text = "Fetching comment votes from vorting portal. Please wait."
    progress_bar = st.progress(0, text=progress_text)

    comment_votes = []
    for idx, comment in enumerate(comments_ids, start=1):
        response = voting.download_comment_votes(comment_id=comment)
        comment_votes.extend(response)
        progress_bar.progress(idx / len(comments_ids), text=progress_text)

    with open('data/comment_votes.json', 'w') as f:
        json.dump(comment_votes, f)

    models.load(con, 'models/silver_comment_votes.sql')

if st.button("Fetch voting results"):
    # TODO find a way to clean the database
    # con.execute("DROP SCHEMA db CASCADE;")
    # con.execute("CREATE SCHEMA IF NOT EXISTS db;")
    # con.execute("USE db;")

    progress_text = "Fetching vorting portal data. Please wait."
    progress_bar = st.progress(0, text=progress_text)


    voting.download_rounds()
    models.load(con, 'models/silver_rounds.sql')
    models.load(con, 'models/silver_rounds_pools.sql')
    progress_bar.progress(0.25, text=progress_text)

    voting.download_pools()
    models.load(con, 'models/silver_pools.sql')
    progress_bar.progress(0.5, text=progress_text)

    fetch_users()
    fetch_comments()
    fetch_proposals(con)
    fetch_milestones(con)
    fetch_reviews(con)
    fetch_comment_votes(con)

    """
    Data successfully loaded
    """

else:
    """
    Data not loaded
    """

uploaded_files = st.file_uploader("Provide the following csv files (`answers.csv`, `questions.csv`, `users.csv`, `wallet-links.csv`):", accept_multiple_files=True)
file_names = [file.name for file in uploaded_files]

print("file_names", file_names)

# Check if "answers.csv" and "questions.csv" are in the uploaded_files list
if ["answers.csv", "questions.csv", "users.csv", "wallet-links.csv"] != file_names:
    # TODO: Load the CSV files into the database
    st.stop()


"""
## Input Data
"""
col1, col2 = st.columns(2)

with col1:
    ratings = con.sql("SELECT * FROM silver_rating").df()
    "### Ratings"
    ratings 

with col2:
    users = con.sql("SELECT * FROM silver_user").df()
    "### Users"
    users

"### Proposals"
proposals = con.sql("SELECT * FROM silver_proposal").df()
proposals


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

