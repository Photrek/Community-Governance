select 
    proposal_id, 
    count(*) as votes_per_proposal,
from {{ ref('int__ratings') }}
where balance > 0
group by proposal_id
