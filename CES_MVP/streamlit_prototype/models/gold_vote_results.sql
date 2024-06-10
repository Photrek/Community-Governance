SELECT
    -- p.proposal_id,
    -- p.title,
    p.question_id,
    p.question,

    COUNT(CASE WHEN r.grade <> 'skip' THEN 1 END) AS num_votes,

    -- need the skipped answers to calculate % of people that voted
    (COUNT(CASE WHEN r.grade <> 'skip' THEN 1 END) * 100.0) / COUNT(r.*) AS percent_voted,

    -- average grade
    NULLIF(
        -- remove skipped votes
        SUM(CASE WHEN r.grade <> 'skip' THEN sqrt(r.total_balance) * CAST(r.grade AS INTEGER) END) / 
        NULLIF(SUM(CASE WHEN r.grade <> 'skip' THEN sqrt(r.total_balance) END), 0), 
    0) AS avg_grade
FROM 
    -- silver_proposals AS p
    bronze_questions AS p
LEFT JOIN 
    -- silver_rating AS r
    bronze_answers AS r
-- ON p.proposal_id = r.proposal_id
ON p.question_id = r.question_id
GROUP BY 
    -- p.proposal_id, 
    -- p.title
    p.question_id,
    p.question