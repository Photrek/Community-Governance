select
    pp.id,
    pp.round_id,
    u.user_name,
    pp.pool_id,
    pp.title,
    pp.content,
    pp.link,
    pp.feature_image,
    pp.requested_amount,
    pp.awarded_amount,
    pp.is_awarded,
    pp.created_at
from 
    stg_pp_proposals pp
join int_proposal_mapping pm
    on pp.id = pm.pp_proposal_id
left join stg_pp_users as u
    on u.user_id = pp.proposer_id