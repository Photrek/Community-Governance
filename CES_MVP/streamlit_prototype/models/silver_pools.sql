SELECT
    id::BIGINT AS id,
    name::VARCHAR AS name,
    description::VARCHAR AS description,
    slug::VARCHAR AS slug,
    REPLACE(max_funding_amount, ',', '')::INTEGER AS max_funding_amount
FROM 
    'data/pools.json'