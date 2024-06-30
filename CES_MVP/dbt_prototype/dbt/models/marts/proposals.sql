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
    {{ ref('stg_pp__proposals') }} pp
join {{ ref('int__proposal_mapping') }} pm
    on pp.id = pm.pp_proposal_id
left join {{ ref('stg_pp__users') }} as u
    on u.user_id = pp.proposer_id
