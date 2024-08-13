with raw_agix_balance_snapshot as (
    SELECT
        id::BIGINT AS id,
        network::VARCHAR AS network,
        address::VARCHAR AS address,
        balance::BIGINT AS balance,
        stake::BIGINT AS stake,
        
        created_on::DATETIME AS created_on,
        updated_on::DATETIME AS updated_on,
    FROM 
        read_csv({{ source('voting_portal', 'agix_balance_snapshot') }})
)

SELECT
    id,
    network,
    address,
    balance,
    stake,
    created_on,
    updated_on,
FROM
    raw_agix_balance_snapshot
WHERE
    id IS NOT NULL
    AND address IS NOT NULL