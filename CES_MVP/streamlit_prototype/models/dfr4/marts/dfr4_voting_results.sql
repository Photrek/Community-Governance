with weighted_sum_of_grades as (
    select
        w.proposal_id,
        sum(w.grade * w.total_voting_weight) as weighted_sum,
        weighted_sum / sum(w.total_voting_weight) as average_grade,
    from
        voting_weights as w
    group by
        w.proposal_id
),

total_voters as (
    select
        count(distinct collection_id) as total_voters
    from
        voting_weights
),

votes_per_proposal as (
    select 
        proposal_id, 
        count(*) as votes_per_proposal,
    from int_ratings
    group by proposal_id
)

select
    w.proposal_id,
    p.title,
    pools.name as pool_name,
    pools.max_funding_amount as pool_funding_amount,
    p.requested_amount,

    vpp.votes_per_proposal,
    tv.total_voters,
    round(vpp.votes_per_proposal / tv.total_voters * 100, 2) as perc_people_that_voted,

    w.weighted_sum,
    w.average_grade,
    average_grade > 6.5 and perc_people_that_voted > 1.0 as eligible,

    -- TODO: use window function to calculate remaining funds by substracting the requested_amount if eligible
    pools.max_funding_amount
from
    proposals as p, total_voters tv
join weighted_sum_of_grades as w
    on w.proposal_id = p.id
join stg_pp_pools as pools
    on p.pool_id = pools.id
join votes_per_proposal as vpp
    on w.proposal_id = vpp.proposal_id
order by
    pool_name,
    average_grade desc
;
