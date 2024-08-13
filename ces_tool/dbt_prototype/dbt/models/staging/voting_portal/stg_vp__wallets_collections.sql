with raw_wallets_collections as (
    SELECT
        collection_id::BIGINT AS collection_id,
        collection_uuid::VARCHAR AS collection_uuid,
        network::VARCHAR AS network,
        address::VARCHAR AS address,
        balance::VARCHAR AS balance,
        created_on::DATETIME AS created_on,
        updated_on::DATETIME AS updated_on,
        
    FROM 
        read_csv({{ source('voting_portal', 'wallets_collections') }})
)

SELECT
    collection_id,
    collection_uuid,
    network,
    address,
    balance,
    created_on,
    updated_on,
FROM
    raw_wallets_collections
WHERE
    collection_id IS NOT NULL
    AND collection_uuid IS NOT NULL
