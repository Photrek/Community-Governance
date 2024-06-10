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
    p.question_id as proposal_id,
    p.question,
    COUNT(CASE WHEN r.grade <> 'skip' THEN 1 END) AS num_votes,

    -- need the skipped answers to calculate % of people that voted
    (COUNT(CASE WHEN r.grade <> 'skip' THEN 1 END) * 100.0) / COUNT(r.*) AS percent_voted,

    -- average grade
    NULLIF(
        {algorithm}
    0) AS avg_grade
FROM 
    stg_vp_questions AS p
LEFT JOIN 
    stg_vp_answers AS r
ON p.question_id = r.question_id

-- can be added once the mapping between question_id and proposal_id is clear
-- WHERE p.round_id = {round_id}

GROUP BY 
    p.question_id, 
    p.question
"""

vote_results = con.sql(query).df()
vote_results

st.bar_chart(data=vote_results, x='proposal_id', y='avg_grade')


"""
Voting Entropy
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
    -- r.proposal_id,
    r.question_id,
                         
    (
        SUM(CASE WHEN r.grade <> 'skip' THEN r.grade::int * e.entropy END)
        / (LOG2(11) * (SELECT total_users FROM max_votes) )
    ) total_entropy,
from
    stg_vp_answers as r
join entropy as e on
    r.collection_id = e.collection_id
group by
    1
order by total_entropy desc
""").df()
voting_entropy

st.bar_chart(data=voting_entropy, x='question_id', y='total_entropy')