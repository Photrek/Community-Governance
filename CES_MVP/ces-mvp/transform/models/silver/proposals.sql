SELECT
    question_id::BIGINT AS proposal_id,
    proposal AS title,
FROM 
    {{ source('bronze', 'questions') }}