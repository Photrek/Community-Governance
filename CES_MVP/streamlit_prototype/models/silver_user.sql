SELECT
    collection_id::BIGINT AS user_id,
    balance::DOUBLE AS balance
FROM 
    'data/users.csv'