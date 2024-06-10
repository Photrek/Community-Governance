with raw_answers as (
    SELECT
        collection_id::BIGINT AS collection_id,
        question_id::BIGINT AS question_id,
        answer::VARCHAR AS grade,
        total_balance::BIGINT AS total_balance
    FROM 
        st_read('data/voting.xlsx', layer = 'Answers')
)

SELECT
    collection_id,
    question_id,
    grade,
    total_balance
FROM
    raw_answers
WHERE
    collection_id IS NOT NULL
    AND question_id IS NOT NULL
    AND grade IS NOT NULL
    AND total_balance IS NOT NULL