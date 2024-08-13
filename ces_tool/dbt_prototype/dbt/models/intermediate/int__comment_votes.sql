select
    u.user_id,
    u.collection_id,
    u.balance,
    count(cv.comment_id) as vote_count,
    -- sum upvotes and downvotes
    sum(case when cv.vote_type = 'upvote' then 1 else 0 end) as upvote_count,
    sum(case when cv.vote_type = 'downvote' then 1 else 0 end) as downvote_count
from
    {{ ref('users') }} as u
left join {{ ref('stg_pp__comment_votes') }} as cv
    on u.user_id = cv.voter_id
group by
    u.user_id,
    u.collection_id,
    u.balance
order by vote_count desc
