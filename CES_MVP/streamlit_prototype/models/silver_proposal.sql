SELECT
    question_id::BIGINT AS proposal_id,
    proposal::VARCHAR AS title,
FROM 
    'data/questions.csv'