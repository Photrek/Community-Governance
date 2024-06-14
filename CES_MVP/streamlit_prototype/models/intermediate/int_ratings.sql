select
    r.collection_id,
    m.pp_proposal_id as proposal_id,

    case
        when r.grade = 'skip' then 0
        else cast(r.grade as int)
    end as grade,
    
    r.total_balance as balance
from
    stg_vp_ratings as r
join int_proposal_mapping as m on
    r.question_id = m.vp_question_id;