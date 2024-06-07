SELECT
    question_id::BIGINT AS question_id,
    question::VARCHAR AS question
FROM 
    st_read('data/voting.xlsx', layer = 'Questions')