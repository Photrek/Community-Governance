SELECT
    collection_id::BIGINT AS collection_id,
    question_id::BIGINT AS question_id,
    answer::VARCHAR AS grade,
    total_balance::BIGINT AS total_balance
FROM 
    st_read('data/voting.xlsx', layer = 'Answers')