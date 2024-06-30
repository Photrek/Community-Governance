select
    r.proposal_id,
    case when min(e.engagement_score) = 0 then 1 else min(e.engagement_score) end as min_engagement_score,
    max(e.engagement_score) as max_engagement_score
from
    {{ ref('int__ratings') }} as r
left join  {{ ref('int__engagement_score') }} as e
    on r.collection_id = e.collection_id
group by
    r.proposal_id
