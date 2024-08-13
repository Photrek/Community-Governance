with user_wallet_mapping as (
    select
        u.user_id,
        u.total_proposals,
        u.user_name,
        u.email,
        u.collection_uuid as user_collection_uuid,
        w.collection_uuid as wallet_address_collection_uuid,
        w.address,
    from
        stg_pp_users as u
    left join stg_vp_wallets_collections as w
        on u.wallet_address = w.address
)

select
    u.user_id,
    u.total_proposals,
    u.user_name,
    u.email,

    cb.collection_id,
    cb.collection_uuid,

    -- convert balance to 0 when not a number otherwise keep the balance as int
    coalesce(cb.balance, 0) as balance,

from
    int_collection_balances as cb

left join user_wallet_mapping as u
    on cb.collection_uuid = u.user_collection_uuid
        or cb.collection_uuid = u.wallet_address_collection_uuid
;