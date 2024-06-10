SELECT
    proposal_id::BIGINT,
    title::VARCHAR,
    status::VARCHAR,
    description::VARCHAR,
    development_description::VARCHAR,
    COALESCE(NULLIF(TRIM(REPLACE(REPLACE(REPLACE(budget, ',', ''), '$', ''), 'USD', '')), ''), NULL)::INTEGER AS budget
FROM 
    'data/milestones.json'