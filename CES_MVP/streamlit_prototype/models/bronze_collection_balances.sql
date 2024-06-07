SELECT
    collection_id::BIGINT AS collection_id,
    collection_uuid::VARCHAR AS collection_uuid,
    balance::BIGINT AS total_balance
FROM 
    st_read('data/voting.xlsx', layer = 'Collections Balances')