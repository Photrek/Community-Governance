select 
    proposal_id, 
    count(*) as votes_per_proposal,
from int_ratings
group by proposal_id