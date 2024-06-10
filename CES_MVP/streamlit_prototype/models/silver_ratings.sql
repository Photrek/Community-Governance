SELECT
    collection_id::BIGINT AS collection_id,

    -- TODO needs to be mapped to proposal_id
    question_id::BIGINT AS question_id,
    
    grade::VARCHAR AS grade,
    total_balance::DOUBLE AS total_balance
FROM 
    bronze_answers