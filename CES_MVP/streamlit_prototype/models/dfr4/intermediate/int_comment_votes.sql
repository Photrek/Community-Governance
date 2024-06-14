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