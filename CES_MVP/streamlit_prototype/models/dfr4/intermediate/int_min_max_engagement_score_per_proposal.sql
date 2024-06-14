select
    r.proposal_id,
    min(e.engagement_score) as min_engagement_score,
    max(e.engagement_score) as max_engagement_score
from
    int_ratings as r
left join int_engagement_score as e
    on r.collection_id = e.collection_id
group by
    r.proposal_id
