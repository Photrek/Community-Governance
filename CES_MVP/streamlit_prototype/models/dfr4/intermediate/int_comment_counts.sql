select
    u.user_id,
    u.collection_id,
    count(c.user_id) as comment_count
from
    users as u
left join stg_pp_comments as c
    on u.user_id = c.user_id
group by
    u.user_id,
    u.collection_id
;