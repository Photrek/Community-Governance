SELECT
    proposal_id::BIGINT AS proposal_id,
    CAST(NULLIF(review_id, '') AS BIGINT) AS review_id,
    reviewer_id::BIGINT AS reviewer_id,
    review_type::VARCHAR AS review_type,
    overall_rating::FLOAT AS overall_rating,
    feasibility_rating::FLOAT AS feasibility_rating,
    desirability_rating::FLOAT AS desirability_rating,
    usefulness_rating::FLOAT AS usefulness_rating,
    CASE WHEN created_at = '' THEN NULL ELSE created_at::DATETIME END AS created_at
    
FROM 
    {{ source('proposal_portal', 'reviews')}}
