import cesdb
import utils

import streamlit as st


con = cesdb.get_db_connection()

# enable streamlit wide mode


"# Deep Funding Round 4 Analysis"


"## General Insights"
col1, col2, col3 = st.columns(3)

col1.metric("Unique Voters", con.sql("select count(distinct collection_uuid) from stg_vp_voting_answers").fetchall()[0][0])
col2.metric("Proposals with Votes", con.sql("select count(distinct question_id) from stg_vp_voting_answers").fetchall()[0][0])
col3.metric(
    "Users with coll id or address",
    con.sql("select count(distinct user_id) from users where collection_id is not null").fetchall()[0][0],
    delta=f"{con.sql('select -1 * count(distinct user_id) from users where collection_id is null').fetchall()[0][0]} without",
)



"""
## Engagement Score

The engagement score per user is calculated as follows:

| Event                             | Weight |
|-----------------------------------|--------|
| comment count                     |      3 |
| upvote count                      |      2 |
| downvote count                    |     -3 |
| reviews created                   |      2 |
| reviews average overall rating    |      2 |
"""

col1, col2, col3 = st.columns(3)
col1.metric("Comments", con.sql("select count(*) from stg_pp_comments").fetchall()[0][0])
col2.metric("Users voting on comments", con.sql("select count(distinct voter_id) from stg_pp_comment_votes").fetchall()[0][0])

st.latex(r"""
         \text{Engagement Score} = 3 \times \text{comment count} + 2 \times \text{upvote count} - 3 \times \text{downvote count}
         """)

engagement_score = con.sql("select * from int_engagement_score").df()
st.dataframe(utils.filter_dataframe(engagement_score), hide_index=True)


"""
## Reputation Weights

The reputation weight is a logarithmic scale that distributes the user engagement score in range [1,5].
"""
st.latex(r"""
         \text{Reputation weight} = 1 + (4 \log\left(\frac{\text{engagement score}}{\text{min engagement score}}\right) / \log\left(\frac{\text{max engagement score}}{\text{min engagement score}}\right))
         """)

reputation_weight = con.sql("select * from int_reputation_weight").df()
st.dataframe(
    utils.filter_dataframe(reputation_weight),
    hide_index=True,
    column_config={
            "proposal_id": st.column_config.NumberColumn(
                "proposal_id",
                format="%d",
            ),
            "collection_id": st.column_config.NumberColumn(
                "collection_id",
                format="%d",
            )
        }    
    )

with st.expander("More details"):
    "### Min/Max engagement score per user"
    int_min_max_engagement_score_per_proposal = con.sql("select * from int_min_max_engagement_score_per_proposal").df()
    st.dataframe(
        utils.filter_dataframe(int_min_max_engagement_score_per_proposal),
        hide_index=True,
        column_config={
            "proposal_id": st.column_config.NumberColumn(
                "proposal_id",
                format="%d",
            )
        }
    )

"""
## Voting Weights
"""
st.latex(r"""
         \text{total voting weight} = \sqrt{\text{balance} / 100000000} \times \text{reputation weight}
         """)

voting_weights = con.sql("select * from voting_weights order by total_voting_weight desc").df()
st.dataframe(
    utils.filter_dataframe(voting_weights),
    hide_index=True,
    column_config={
            "proposal_id": st.column_config.NumberColumn(
                "proposal_id",
                format="%d",
            )
        }
    )

"""
## Voting Results

The voting results are calculated as follows:
"""

st.latex(r"""
eligable = \begin{cases}
   true &\text{if } \text{average\_grade} > 6.5 \text{ and } \text{percent\_of\_people\_voted} > 1.0 \\
   false &\text{otherwise}
\end{cases}
""")

voting_results = con.sql("""
                         select 
                            proposal_id,
                            title,
                            pool_id,
                            pool_name,
                            pool_funding_amount,
                            requested_amount,
                            votes_per_proposal,
                            total_voters,
                            perc_people_that_voted,
                            weighted_sum,
                            average_grade,
                            eligible,
                            max_funding_amount,

                         from dfr4_voting_results
                         """).df()
st.dataframe(
    utils.filter_dataframe(voting_results),
    hide_index=True,
    column_config={
            "proposal_id": st.column_config.NumberColumn(
                "proposal_id",
                format="%d",
            )
        }
    )

with st.expander("More details"):

    "### Votes per grade"
    voting_results = con.sql("""
                         select 
                            proposal_id,
                            title,
                            votes_per_proposal,
                            total_voters,
                            perc_people_that_voted,
                            weighted_sum,
                            average_grade,
                             
                            grade_sum,
                            grade_1,
                            grade_2,
                            grade_3,
                            grade_4,
                            grade_5,
                            grade_6,
                            grade_7,
                            grade_8,
                            grade_9,
                            grade_10,
                            average_grade_2,
                            simple_average_grade,

                         from dfr4_voting_results
                         """).df()
    st.dataframe(
        utils.filter_dataframe(voting_results),
        hide_index=True,
        column_config={
                "proposal_id": st.column_config.NumberColumn(
                    "proposal_id",
                    format="%d",
                )
            }
        )


    "### Votes per proposal"
    int_votes_per_proposal = con.sql("select * from int_votes_per_proposal").df()
    st.dataframe(
        utils.filter_dataframe(int_votes_per_proposal),
        hide_index=True,
        column_config={
            "proposal_id": st.column_config.NumberColumn(
                "proposal_id",
                format="%d",
            )
        }
    )

st.stop()

"### Voting results per pool"
option = utils.round_selector(index=3)
round_id = option[0]

pools_query = f"""
select
    p.id,
    p.name,
    p.max_funding_amount
from
    stg_pp_pools as p
left join stg_pp_rounds_pools rp
    on p.id = rp.pool_id
where
    rp.round_id = {round_id}
"""
pools = con.sql(pools_query).df()

for index, row in pools.iterrows():
    pool_id = row['id']
    pool_name = row['name']
    pool_max_funding = row['max_funding_amount']

    f"""
    ### {pool_id} - {pool_name}

    Max Funding: {pool_max_funding}
    """
    query = f"select * from dfr4_voting_results where pool_id = {pool_id}"
    voting_results = con.sql(query).df()
    st.dataframe(
        voting_results,
        hide_index=True,
        column_config={
            "proposal_id": st.column_config.NumberColumn(
                "proposal_id",
                format="%d",
            )
        }
    )

st.stop()

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