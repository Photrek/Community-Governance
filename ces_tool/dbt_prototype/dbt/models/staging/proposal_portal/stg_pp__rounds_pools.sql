SELECT DISTINCT
    round_id::BIGINT AS round_id,
    pool_id::BIGINT AS pool_id
FROM 
    {{ source('proposal_portal', 'rounds_pools')}}
