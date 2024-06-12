with user_voting_weight as (
    select
        uces.collection_id,
        uces.user_id,
        uces.contribution_engagement_score * 0.05 as voting_weight
    from
        int_user_contribution_engagement_score as uces
),

-- total voting weight per proposal
total_voting_weight as (
    select
        r.proposal_id,
        sum(uvw.voting_weight) as total_voting_weight,
    from
        int_ratings as r
    left join user_voting_weight as uvw
        on r.collection_id = uvw.collection_id
    where
        r.grade <> 'skip'
    group by
        r.proposal_id,
),

min_max_voting_weight_per_proposal as (
    select
        r.proposal_id,
        min(uvw.voting_weight) as min_voting_weight,
        max(uvw.voting_weight) as max_voting_weight
    from
        int_ratings as r
    left join user_voting_weight as uvw
        on r.collection_id = uvw.collection_id
    group by
        r.proposal_id
)

-- 
select
    r.proposal_id,
    (mm.min_voting_weight + sum(uvw.voting_weight / tvw.total_voting_weight) * (mm.max_voting_weight - mm.min_voting_weight)) as reputation_voting_weight,
    sum(uvw.voting_weight / tvw.total_voting_weight) as voting_fraction,
    mm.min_voting_weight,
    mm.max_voting_weight
from
    int_ratings as r
left join user_voting_weight as uvw
    on r.collection_id = uvw.collection_id
left join total_voting_weight as tvw
    on r.proposal_id = tvw.proposal_id
left join min_max_voting_weight_per_proposal as mm
    on r.proposal_id = mm.proposal_id
where
    r.grade <> 'skip'
group by
    r.proposal_id,
    mm.min_voting_weight,
    mm.max_voting_weight
;




-- select
--     r.proposal_id,
--     uvw.collection_id,
--     uvw.voting_weight,
--     tvw.total_voting_weight,
-- from
--     int_ratings as r
-- left join user_voting_weight as uvw
--     on r.collection_id = uvw.collection_id
-- left join total_voting_weight as tvw
--     on r.proposal_id = tvw.proposal_id
-- where
--     r.grade <> 'skip'
