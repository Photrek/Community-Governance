with votes as (
    select
        w.proposal_id,
        w.total_voting_weight,
        w.grade,
        w.total_voting_weight_wo_reputation,
    from
        {{ ref('voting_weights') }} as w
    where
        w.grade <> 0
),

weighted_sum_of_grades as (
    select
        w.proposal_id,

        -- final computation
        sum(w.grade * w.total_voting_weight) as weighted_sum,
        weighted_sum / case when sum(w.total_voting_weight) = 0 then 1 else sum(w.total_voting_weight) end as average_grade,

        -- final computation ignoring reputation score to compare to previous calculations
        sum(w.grade * w.total_voting_weight_wo_reputation) as weighted_sum_wo_reputation,
        weighted_sum_wo_reputation / case when sum(w.total_voting_weight_wo_reputation) = 0 then 1 else sum(w.total_voting_weight_wo_reputation) end as average_grade_wo_reputation,

        -- debug information to check if average_grade is correct
        sum(w.grade) / count(w.grade) as simple_average_grade,

        SUM(CASE WHEN w.grade = 1 THEN w.total_voting_weight ELSE 0 END) AS grade_1,
        SUM(CASE WHEN w.grade = 2 THEN w.total_voting_weight ELSE 0 END) AS grade_2,
        SUM(CASE WHEN w.grade = 3 THEN w.total_voting_weight ELSE 0 END) AS grade_3,
        SUM(CASE WHEN w.grade = 4 THEN w.total_voting_weight ELSE 0 END) AS grade_4,
        SUM(CASE WHEN w.grade = 5 THEN w.total_voting_weight ELSE 0 END) AS grade_5,
        SUM(CASE WHEN w.grade = 6 THEN w.total_voting_weight ELSE 0 END) AS grade_6,
        SUM(CASE WHEN w.grade = 7 THEN w.total_voting_weight ELSE 0 END) AS grade_7,
        SUM(CASE WHEN w.grade = 8 THEN w.total_voting_weight ELSE 0 END) AS grade_8,
        SUM(CASE WHEN w.grade = 9 THEN w.total_voting_weight ELSE 0 END) AS grade_9,
        SUM(CASE WHEN w.grade = 10 THEN w.total_voting_weight ELSE 0 END) AS grade_10,
        grade_1 + grade_2 + grade_3 + grade_4 + grade_5 + grade_6 + grade_7 + grade_8 + grade_9 + grade_10 as grade_sum,

        (
            (
                (grade_1 * 1)
                + (grade_2 * 2)
                + (grade_3 * 3)
                + (grade_4 * 4)
                + (grade_5 * 5)
                + (grade_6 * 6)
                + (grade_7 * 7)
                + (grade_8 * 8)
                + (grade_9 * 9)
                + (grade_10 * 10)
            ) / case when grade_sum = 0 then 1 else grade_sum end
        ) as average_grade_2
    from
        votes as w
    group by
        w.proposal_id
),

total_voters as (
    select
        count(distinct collection_id) as total_voters
    from
        {{ ref('voting_weights') }}
    where
        balance > 0
)

select
    w.proposal_id,
    p.title,
    p.link as proposal_url,
    p.user_name as proposer_name,
    pools.id as pool_id,
    pools.name as pool_name,
    pools.max_funding_amount as pool_funding_amount,
    p.requested_amount,

    vpp.votes_per_proposal,
    tv.total_voters,
    round(vpp.votes_per_proposal / tv.total_voters * 100, 2) as perc_people_that_voted,

    w.weighted_sum,
    w.average_grade,
    average_grade > 6.5 and perc_people_that_voted > 1.0 as eligible,

    w.average_grade_wo_reputation,

    -- TODO: use window function to calculate remaining funds by substracting the requested_amount if eligible
    pools.max_funding_amount,

    w.grade_sum,
    w.grade_1,
    w.grade_2,
    w.grade_3,
    w.grade_4,
    w.grade_5,
    w.grade_6,
    w.grade_7,
    w.grade_8,
    w.grade_9,
    w.grade_10,
    w.average_grade_2,
    w.simple_average_grade,
from
    {{ ref('proposals') }} as p, total_voters tv
join weighted_sum_of_grades as w
    on w.proposal_id = p.id
join {{ ref('stg_pp__pools') }} as pools
    on p.pool_id = pools.id
join {{ ref('int__votes_per_proposal') }} as vpp
    on w.proposal_id = vpp.proposal_id
order by
    pool_name,
    average_grade desc
