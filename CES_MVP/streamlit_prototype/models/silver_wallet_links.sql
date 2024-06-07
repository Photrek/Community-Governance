SELECT
    address::VARCHAR AS wallet_address,
    collection_id::BIGINT AS collection_id,
    balance::BIGINT AS balance
FROM 
    'data/wallet_links.csv'