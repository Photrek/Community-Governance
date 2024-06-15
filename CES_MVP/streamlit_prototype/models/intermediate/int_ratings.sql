select
    c.collection_id,
    m.pp_proposal_id as proposal_id,

    case
        when r.grade = 'skip' then 0
        else cast(r.grade as int)
    end as grade,
    
    b.balance
from
    stg_vp_voting_answers as r
left join stg_vp_wallets_collections as c
    on r.collection_uuid = c.collection_uuid
left join int_collection_balances as b
    on r.collection_uuid = b.collection_uuid
join int_proposal_mapping as m on
    r.question_id = m.vp_question_id
;