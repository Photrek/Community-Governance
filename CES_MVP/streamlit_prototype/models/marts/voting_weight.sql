select
    r.proposal_id,
    sqrt(r.balance) * rvw.reputation_voting_weight as final_voting_weight
from 
    int_ratings as r
left join int_reputation_voting_weight as rvw
    on r.proposal_id = rvw.proposal_id
;