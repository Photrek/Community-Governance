select
    r.proposal_id,
    min(e.engagement_score) as tmp_min_engagement_score,
    case when tmp_min_engagement_score = 0 then 1 else tmp_min_engagement_score end as min_engagement_score,
    max(e.engagement_score) as max_engagement_score
from
    int_ratings as r
left join int_engagement_score as e
    on r.collection_id = e.collection_id
group by
    r.proposal_id
;