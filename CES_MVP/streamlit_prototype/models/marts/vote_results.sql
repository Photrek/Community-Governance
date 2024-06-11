SELECT
    p.id as proposal_id,
    p.title,

    COUNT(CASE WHEN r.grade <> 'skip' THEN 1 END) AS num_votes,

    -- need the skipped answers to calculate % of people that voted
    (COUNT(CASE WHEN r.grade <> 'skip' THEN 1 END) * 100.0) / COUNT(r.*) AS percent_voted,

    -- average grade
    NULLIF(
        -- remove skipped votes
        SUM(CASE WHEN r.grade <> 'skip' THEN sqrt(r.balance) * CAST(r.grade AS INTEGER) END) / 
        NULLIF(SUM(CASE WHEN r.grade <> 'skip' THEN sqrt(r.balance) END), 0), 
    0) AS avg_grade
FROM 
    proposals AS p
LEFT JOIN int_ratings AS r
    ON p.id = r.proposal_id
GROUP BY 
    p.id, 
    p.title
;