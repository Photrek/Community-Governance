with raw_voting_questions as (
    SELECT
        id::BIGINT AS id,
        question_id::VARCHAR AS question_id,
        pool_id::BIGINT AS pool_id,
        short_name::VARCHAR AS short_name,
        heading::VARCHAR AS heading,
        question::VARCHAR AS question,
        description::VARCHAR AS description,
        details_url::VARCHAR AS details_url,
        created_on::DATETIME AS created_on,
        updated_on::DATETIME AS updated_on,
        end_time::DATETIME AS end_time,
        
    FROM 
        read_csv('data/voting_questions.csv')
)

SELECT
    id,
    question_id,
    pool_id,
    -- short_name,
    -- heading,

    -- extract proposal title from question html content like: <embed><div style=""display: flex; align-items: center; gap: 20px""><div style=""width: 150px; height: 100px; display: flex; align-items: center; ""><img style=""object-fit: contain;"" src=""https://deepfunding.ai/wp-content/uploads/2024/04/5403cd545ff9c722af07ab1fa3f21355_deepfund-1.png"" alt=""""></div><div><b>SkinScan AI: Canine Dermatologic Diagnosis</b><br> Funding Request: $150,000<br> Proposer: VeterinaryDAO<br> Pitch Video: <a href=""https://www.youtube.com/watch?v=6adtG6fpgas"">https://www.youtube.com/watch?v=6adtG6fpgas</a></div></div><input readOnly class=""rating"" style=""--value: 5"" type=""range"" /></embed>
    regexp_extract(question, '.*<b>([^<]*)', 1) as proposal_title,
    -- question,
    -- description,
    details_url,
    created_on,
    updated_on,
    end_time,
FROM
    raw_voting_questions
WHERE
    id IS NOT NULL
    AND question_id IS NOT NULL
    AND details_url IS NOT NULL
;