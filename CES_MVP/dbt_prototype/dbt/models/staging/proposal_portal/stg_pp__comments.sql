SELECT
    comment_id::BIGINT AS id,
    user_id::BIGINT AS user_id,
    proposal_id::BIGINT AS proposal_id,
    content::VARCHAR AS content,

    -- fix empty strings in comment_votes
    CASE 
        WHEN comment_votes = '' THEN 0
        ELSE comment_votes::INTEGER
    END AS comment_votes,

    created_at::DATETIME AS created_at,
    updated_at::DATETIME AS updated_at
FROM 
    {{ source('proposal_portal', 'comments')}}