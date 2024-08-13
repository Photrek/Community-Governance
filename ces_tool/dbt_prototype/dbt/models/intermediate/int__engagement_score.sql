select 
    cv.user_id,
    cv.collection_id,
    cv.balance,
    c.comment_count,
    cv.upvote_count,
    cv.downvote_count,

    -- add count of reviews
    count(r.reviewer_id) as review_count,

    -- add average overall_rating score
    coalesce(avg(r.overall_rating), 0) as average_review_overall_rating,
    
    -- TODO: add more signals as defined in https://docs.google.com/document/d/1Kz7YPG03eaqYJlRbg0FnQlExxM5nb-57KM1sE53WfbM
    (c.comment_count * 3.0) 
    + (cv.upvote_count * 2.0) 
    + (cv.downvote_count * -3.0)
    + (review_count * 2)
    -- + (average_review_overall_rating * 2)
        as engagement_score
from
    {{ ref('int__comment_votes') }} as cv
left join {{ ref('int__comment_counts') }} as c
    on cv.user_id = c.user_id
left join {{ ref('stg_pp__reviews') }} as r
    on cv.user_id = r.reviewer_id
group by
    cv.user_id,
    cv.collection_id,
    cv.balance,
    c.comment_count,
    cv.upvote_count,
    cv.downvote_count
