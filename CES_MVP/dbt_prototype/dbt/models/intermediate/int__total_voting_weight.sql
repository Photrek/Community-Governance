select
    r.proposal_id,
    sum(e.engagement_score) as total_engagement_score,
from
    {{ ref('int__ratings') }} as r
left join {{ ref('int__engagement_score') }} as e
    on r.collection_id = e.collection_id
where
    -- ignore skipped votes
    r.grade <> 0
group by
    r.proposal_id