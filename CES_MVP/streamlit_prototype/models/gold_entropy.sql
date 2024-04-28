with total_votes as (
    select
        user_id,
        count(*) as total_votes
    from
        silver_rating
    group by
        user_id
),

-- probability of a user voting a certain grade
probabilities as (
    select
        r.user_id,
        (
            (count(grade) / v.total_votes)
            * LOG2(count(grade) / v.total_votes)
        ) as propability,
    from
        silver_rating as r
    join total_votes as v on
        r.user_id = v.user_id
    group by
        r.user_id,
        v.total_votes,
        grade
),

entropies as (

    select 
        user_id,
        -sum(propability) as entropy
    from 
        probabilities
    group by
        user_id
)

select 
    user_id,
    -- normalize by dividing with the maximum possible value of voting entropy
    entropy / LOG2(11) as entropy
from
    entropies;
-- where
--     user_id = 789
--     or user_id = 9;