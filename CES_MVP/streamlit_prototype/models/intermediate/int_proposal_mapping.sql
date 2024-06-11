-- map Voting Portal questions to Proposal Portal proposals
SELECT
    vp.question_id AS vp_question_id,
    vp.question AS vp_title,
    pp.id AS pp_proposal_id,
    pp.title AS pp_title,

    -- due to mismatching question_id and proposal_id, we need
    -- to calculate the distance between the two strings
    levenshtein(vp.question, pp.title) AS distance
FROM
    stg_vp_questions vp
CROSS JOIN
    stg_pp_proposals pp
WHERE
    distance < 5;