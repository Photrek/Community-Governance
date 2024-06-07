SELECT
    address::VARCHAR AS wallet_address,
    collection_id::BIGINT AS collection_id,
    balance::BIGINT AS total_balance
FROM 
    st_read('data/voting.xlsx', layer = 'Collections')