SELECT
    id::BIGINT AS id,
    name::VARCHAR AS name,
    slug::VARCHAR AS slug
FROM 
    {{ source('proposal_portal', 'rounds')}}