SELECT
    round_id::BIGINT AS round_id,
    pool_id::BIGINT AS pool_id
FROM 
    'data/rounds_pools.json'