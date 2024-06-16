select
    cb.collection_id,
    m.pp_proposal_id as proposal_id,

    case
        when r.grade = 'skip' then 0
        else cast(r.grade as int)
    end as grade,
    
    coalesce(cb.balance, 0) as balance,
from
    stg_vp_voting_answers as r
left join int_collection_balances as cb
    on r.collection_uuid = cb.collection_uuid
left join int_proposal_mapping as m on
    r.question_id = m.vp_question_id
;