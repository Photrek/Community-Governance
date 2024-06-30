with raw_answers as (
    SELECT
        collection_id::VARCHAR AS collection_uuid,
        question_id::BIGINT AS question_id,
        answer::VARCHAR AS grade,
        balance::BIGINT AS total_balance
    FROM 
        read_csv({{ source('voting_portal', 'voting_answers') }})
)

SELECT
    collection_uuid,
    question_id,
    grade,
    total_balance
FROM
    raw_answers
WHERE
    collection_uuid IS NOT NULL
    AND question_id IS NOT NULL
    AND grade IS NOT NULL
    AND total_balance IS NOT NULL