SELECT
    comment_id::BIGINT AS comment_id,
    
    -- refers to user_id doing the voting
    voter_id::BIGINT AS voter_id,
    vote_type::VARCHAR AS vote_type,
FROM 
    'data/comment_votes.json'