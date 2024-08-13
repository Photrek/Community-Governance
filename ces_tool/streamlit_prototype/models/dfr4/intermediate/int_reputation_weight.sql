select
    r.collection_id,
    r.proposal_id,
    coalesce(e.engagement_score, 0) as engagement_score,

    mm.min_engagement_score,
    mm.max_engagement_score,

    -- reputation weight = engagement_score scaled between 1 and 5
    coalesce(
        case when e.engagement_score = 0 then 1 else 1 + (
            4 * log(e.engagement_score / mm.min_engagement_score)
            / log(mm.max_engagement_score / mm.min_engagement_score)
        ) end, 1) as reputation_weight,
from
    int_ratings as r
left join int_engagement_score as e
    on r.collection_id = e.collection_id
left join int_min_max_engagement_score_per_proposal as mm
    on r.proposal_id = mm.proposal_id
;