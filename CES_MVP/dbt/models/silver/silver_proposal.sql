SELECT
    question_id::BIGINT AS proposal_id,
    proposal::VARCHAR AS title,
FROM 
    {{ ref('bronze_question') }}