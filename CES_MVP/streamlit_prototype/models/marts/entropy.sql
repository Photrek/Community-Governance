with total_votes as (
    select
        collection_id,
        count(*) as total_votes
    from
        stg_vp_answers
    group by
        collection_id
),

-- probability of a user voting a certain grade
probabilities as (
    select
        r.collection_id,
        (
            (count(grade) / v.total_votes)
            * LOG2(count(grade) / v.total_votes)
        ) as propability,
    from
        stg_vp_answers as r
    join total_votes as v on
        r.collection_id = v.collection_id
    group by
        r.collection_id,
        v.total_votes,
        grade
),

entropies as (

    select 
        collection_id,
        -sum(propability) as entropy
    from 
        probabilities
    group by
        collection_id
)

select 
    collection_id,
    -- normalize by dividing with the maximum possible value of voting entropy
    entropy / LOG2(11) as entropy
from
    entropies;