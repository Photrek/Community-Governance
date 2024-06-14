select
    r.collection_id,
    r.proposal_id,
    r.grade,
    r.balance,

    e.engagement_score,
    sqrt(r.balance/100000000) as sqrt_balance,
    rw.reputation_weight,
    sqrt_balance * rw.reputation_weight as total_voting_weight
from
    int_ratings as r
join int_reputation_weight as rw
    on r.proposal_id = rw.proposal_id
join int_engagement_score as e
    on r.collection_id = e.collection_id