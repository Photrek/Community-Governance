-- up & down votes per user
with comment_votes as (
    select
        u.user_id,
        u.collection_id,
        -- sum upvotes and downvotes
        sum(case when cv.vote_type = 'upvote' then 1 else 0 end) as upvote_count,
        sum(case when cv.vote_type = 'downvote' then 1 else 0 end) as downvote_count
    from
        users as u
    left join stg_pp_comment_votes as cv
        on u.user_id = cv.voter_id
    group by
        u.user_id,
        u.collection_id
),

-- amount of comment per user
comments as (
    select
        u.user_id,
        u.collection_id,
        count(c.*) as comment_count
    from
        users as u
    left join stg_pp_comments as c
        on u.user_id = c.user_id
    group by
        u.user_id,
        u.collection_id
)

select 
    cv.user_id,
    cv.collection_id,
    c.comment_count,
    cv.upvote_count,
    cv.downvote_count,
    
    (c.comment_count * 3.0) + (cv.upvote_count * 2.0) + (cv.downvote_count * -3.0) as contribution_engagement_score
from
    comment_votes as cv
join comments as c
    on cv.user_id = c.user_id
;