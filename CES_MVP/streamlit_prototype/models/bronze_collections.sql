with raw_collections as (
    SELECT
        address::VARCHAR AS wallet_address,
        collection_id::BIGINT AS collection_id,
        balance::BIGINT AS total_balance
    FROM 
        st_read('data/voting.xlsx', layer = 'Collections')
)

SELECT
    wallet_address,
    collection_id,
    total_balance
FROM
    raw_collections
WHERE
    collection_id IS NOT NULL
    AND wallet_address IS NOT NULL
    AND total_balance IS NOT NULL