select
    r.collection_uuid,
    cb.collection_id,
    m.pp_proposal_id as proposal_id,

    case
        when r.grade = 'skip' then null
        else cast(r.grade as int)
    end as grade,
    
    coalesce(cb.balance, 0) as balance,
from
    {{ ref('stg_vp__voting_answers') }} as r
left join {{ ref('int__collection_balances') }} as cb
    on r.collection_uuid = cb.collection_uuid
left join {{ ref('int__proposal_mapping') }} as m on
    r.question_id = m.vp_question_id
where r.grade <> 'skip'
