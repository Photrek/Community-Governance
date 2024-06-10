with raw_questions as (
    SELECT
        question_id::BIGINT AS question_id,
        question::VARCHAR AS question
    FROM 
        st_read('data/voting.xlsx', layer = 'Questions')
)

SELECT
    question_id,
    question
FROM
    raw_questions
WHERE
    question_id IS NOT NULL
    AND question IS NOT NULL
