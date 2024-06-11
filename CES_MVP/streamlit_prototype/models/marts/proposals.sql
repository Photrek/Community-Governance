SELECT
    pp.id,
    pp.round_id,
    pp.pool_id,
    pp.title,
    pp.content,
    pp.link,
    pp.feature_image,
    pp.requested_amount,
    pp.awarded_amount,
    pp.is_awarded,
    pp.created_at
FROM 
    stg_pp_proposals pp
JOIN
    int_proposal_mapping pm
ON
    pp.id = pm.pp_proposal_id