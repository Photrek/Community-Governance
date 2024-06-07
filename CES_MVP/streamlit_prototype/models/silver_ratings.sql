SELECT
    collection_id::BIGINT AS collection_id,
    question_id::BIGINT AS proposal_id,
    answer::VARCHAR AS grade,
    total_balance::DOUBLE AS total_balance
FROM 
    'data/votes.csv'