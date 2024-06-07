SELECT
    id::BIGINT AS user_id,
    user_name::VARCHAR AS user_name,
    email::VARCHAR AS email,

    -- split wallt_address into collection_id and wallet_address because the collection_id field is not verified
    -- and some users put their wallet address and some their collection_d
    CASE 
        WHEN collection_id ~ '^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$' THEN collection_id::VARCHAR
        ELSE NULL
    END AS collection_id,

    CASE 
        WHEN collection_id ~ '^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$' THEN NULL
        WHEN collection_id = 'N/A' THEN NULL
        ELSE collection_id::VARCHAR
    END AS wallet_address,

    total_proposals::INTEGER AS total_proposals
FROM 
    'data/users.json'
