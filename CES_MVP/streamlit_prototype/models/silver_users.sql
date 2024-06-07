SELECT
    id::BIGINT AS user_id,
    user_name::VARCHAR AS user_name,
    email::VARCHAR AS email,

    CASE 
        WHEN collection_id = 'N/A' THEN NULL
        ELSE collection_id::VARCHAR
    END AS wallet_address,

    total_proposals::INTEGER AS total_proposals
FROM 
    'data/users.json'