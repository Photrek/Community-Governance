with agix_distribution as (
    select
        r.collection_id,
        r.balance * 0.1 as agix_reward,
    from
        int_ratings as r
),

-- total agix reward for all eligible users
total_agix_reward as (
    select
        r.proposal_id,
        sum(ad.agix_reward) as total_agix_reward,
    from
        int_ratings as r
    left join agix_distribution as ad
        on r.collection_id = ad.collection_id
    where
        r.grade <> 'skip'
    group by
        r.proposal_id
)

select
    r.proposal_id,
    ad.collection_id,
    ad.agix_reward,
    tar.total_agix_reward,
    
    ad.agix_reward / tar.total_agix_reward as agix_fraction,
    agix_fraction * tar.total_agix_reward as final_agix_reward
from
    int_ratings as r
left join agix_distribution as ad
    on r.collection_id = ad.collection_id
left join total_agix_reward as tar
    on r.proposal_id = tar.proposal_id
where
    r.grade <> 'skip'
;