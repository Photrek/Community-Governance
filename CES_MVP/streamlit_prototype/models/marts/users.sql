select
    COALESCE(cb.collection_id, c.collection_id) as collection_id,
    u.user_id,
    u.total_proposals,
    cb.total_balance as balance

from
    stg_pp_users as u

left join stg_vp_collection_balances as cb
    on u.collection_uuid = cb.collection_uuid

left join stg_vp_collections as c
    on u.wallet_address = c.wallet_address