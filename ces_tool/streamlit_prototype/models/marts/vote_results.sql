SELECT
    p.id as proposal_id,
    p.title,

    COUNT(r.grade) AS num_votes,

    -- need the skipped answers to calculate % of people that voted
    (COUNT(r.grade) * 100.0) / COUNT(r.*) AS percent_voted,

    -- average grade
    NULLIF(
        -- remove skipped votes
        SUM(sqrt(r.balance) * r.grade) / 
        NULLIF(SUM(sqrt(r.balance)), 0), 
    0) AS avg_grade
FROM 
    proposals AS p
LEFT JOIN int_ratings AS r
    ON p.id = r.proposal_id
GROUP BY 
    p.id, 
    p.title
;