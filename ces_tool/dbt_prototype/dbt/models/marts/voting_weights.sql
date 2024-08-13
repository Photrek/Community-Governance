select
    r.collection_id,
    r.collection_uuid,
    r.proposal_id,
    r.grade,
    r.balance,
    
    sqrt(r.balance/100000000) as sqrt_balance,
    rw.reputation_weight,
    sqrt_balance * rw.reputation_weight as total_voting_weight,
    
    -- voting without ignoring reputation to be able to compare to previous calculations
    sqrt_balance as total_voting_weight_wo_reputation
from
    {{ ref('int__ratings') }} as r

-- Have to use left join here because not all proposals have engagement scores?
left join {{ ref('int__reputation_weight') }} as rw
    on r.proposal_id = rw.proposal_id 
        and r.collection_id = rw.collection_id
