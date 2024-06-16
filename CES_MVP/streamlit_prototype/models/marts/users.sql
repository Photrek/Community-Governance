select
    -- use cb.collection_id when available, otherwise use w.collection_id
    coalesce(cb.collection_id, w.collection_id) as collection_id,

    u.user_id,
    u.total_proposals,

    -- convert balance to 0 when not a number otherwise keep the balance as int
    coalesce(cb.balance, 0) as balance,

from
    stg_pp_users as u

left join int_collection_balances as cb
    on u.collection_uuid = cb.collection_uuid
left join stg_vp_wallets_collections as w
    on u.wallet_address = w.address
;