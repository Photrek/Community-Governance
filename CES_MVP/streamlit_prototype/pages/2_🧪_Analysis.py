import cesdb
import utils

import streamlit as st


con = cesdb.get_db_connection()

"""
# 🧪 User Engagement Analysis
"""

option = utils.round_selector()
round_id = option[0]

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
        SUM(CASE WHEN r.grade <> 'skip' THEN sqrt(r.balance) * CAST(r.grade AS INTEGER) END) / 
        NULLIF(SUM(CASE WHEN r.grade <> 'skip' THEN sqrt(r.balance) END), 0),
    """
else:
    algorithm = """
        -- remove skipped votes
        SUM(CASE WHEN r.grade <> 'skip' THEN CAST(r.grade AS INTEGER) END) / 
        NULLIF(COUNT(CASE WHEN r.grade <> 'skip' THEN 1 END), 0), 
    """

query = f"""
SELECT
    p.id,
    p.title,
    COUNT(CASE WHEN r.grade <> 'skip' THEN 1 END) AS num_votes,

    -- need the skipped answers to calculate % of people that voted
    (COUNT(CASE WHEN r.grade <> 'skip' THEN 1 END) * 100.0) / COUNT(r.*) AS percent_voted,

    -- average grade
    NULLIF(
        {algorithm}
    0) AS avg_grade
FROM 
    proposals AS p
LEFT JOIN 
    int_ratings AS r
ON p.id = r.proposal_id

-- can be added once the mapping between question_id and proposal_id is clear
WHERE p.round_id = {round_id}

GROUP BY 
    p.id, 
    p.title
"""

vote_results = con.sql(query).df()
vote_results

st.bar_chart(data=vote_results, x='id', y='avg_grade')


"""
# Voting Entropy
"""

voting_entropy = con.sql("SELECT * FROM entropy").df()
voting_entropy

st.bar_chart(data=voting_entropy, x='collection_id', y='entropy')


voting_entropy = con.sql("""
with max_votes as (
    select
        count(*) as total_users
    from
        --stg_pp_user
        stg_vp_collections
)

select 
    r.proposal_id,
                         
    (
        SUM(CASE WHEN r.grade <> 'skip' THEN r.grade::int * e.entropy END)
        / (LOG2(11) * (SELECT total_users FROM max_votes) )
    ) total_entropy,
from
    int_ratings as r
join entropy as e on
    r.collection_id = e.collection_id
group by
    1
order by total_entropy desc
""").df()
voting_entropy

st.bar_chart(data=voting_entropy, x='proposal_id', y='total_entropy')