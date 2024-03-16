SELECT
    collection_id::BIGINT AS user_id,
    question_id::BIGINT AS proposal_id,
    answer AS grade,
    total_balance::double AS total_balance
FROM 
    {{ source('bronze', 'answers') }}