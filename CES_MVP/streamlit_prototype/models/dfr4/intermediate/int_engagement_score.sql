select 
    cv.user_id,
    cv.collection_id,
    c.comment_count,
    cv.upvote_count,
    cv.downvote_count,
    
    -- TODO: add more signals as defined in https://docs.google.com/document/d/1Kz7YPG03eaqYJlRbg0FnQlExxM5nb-57KM1sE53WfbM
    (c.comment_count * 3.0) 
    + (cv.upvote_count * 2.0) 
    + (cv.downvote_count * -3.0) as engagement_score
from
    int_comment_votes as cv
join int_comment_counts as c
    on cv.user_id = c.user_id
;