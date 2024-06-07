SELECT
    id::BIGINT AS id,
    name::VARCHAR AS name,
    slug::VARCHAR AS slug
FROM 
    'data/rounds.json'