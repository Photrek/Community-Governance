SELECT
    id::BIGINT AS id,
    round_id::BIGINT AS round_id,
    pool_id::BIGINT AS pool_id,
    proposer_id::BIGINT AS proposer_id,
    title::VARCHAR AS title,
    content::VARCHAR AS content,
    link::VARCHAR AS link,
    feature_image::VARCHAR AS feature_image,
    REPLACE(REPLACE(requested_amount, ',', ''), '$', '')::INTEGER AS requested_amount,

    -- handle empty strings in awarded_amount
    CASE 
        WHEN awarded_amount = '' THEN 0
        ELSE REPLACE(REPLACE(awarded_amount, ',', ''), '$', '')::INTEGER
    END AS awarded_amount,

    is_awarded::BOOLEAN AS is_awarded,

    created_at::DATETIME AS created_at
FROM 
    'data/proposals.json'