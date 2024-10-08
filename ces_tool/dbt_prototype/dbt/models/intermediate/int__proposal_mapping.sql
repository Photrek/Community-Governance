-- map Voting Portal questions to Proposal Portal proposals
SELECT
    vp.question_id AS vp_question_id,
    vp.proposal_title AS vp_title,
    pp.id AS pp_proposal_id,
    pp.title AS pp_title,

    -- due to mismatching question_id and proposal_id, we need
    -- to calculate the distance between the two strings
    levenshtein(vp.proposal_title, pp.title) AS distance
FROM
    {{ ref('stg_vp__voting_questions') }} vp
left JOIN {{ ref('stg_pp__proposals') }} pp
    on vp.details_url = pp.link
