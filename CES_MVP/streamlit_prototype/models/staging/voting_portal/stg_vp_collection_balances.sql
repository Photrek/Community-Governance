WITH raw_collection_balances as (
    SELECT
        collection_id::BIGINT AS collection_id,
        collection_uuid::VARCHAR AS collection_uuid,
        balance::BIGINT AS total_balance
    FROM 
        st_read('data/voting.xlsx', layer = 'Collections Balances')
)

SELECT
    collection_id,
    collection_uuid,
    total_balance
FROM
    raw_collection_balances
WHERE
    collection_id IS NOT NULL

    -- TODO: for now collection_id is optional
    -- AND collection_uuid IS NOT NULL
    
    AND total_balance IS NOT NULL