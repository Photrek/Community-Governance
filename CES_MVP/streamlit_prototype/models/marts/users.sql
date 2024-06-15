select
    cb.collection_id,
    u.user_id,
    u.total_proposals,
    cb.balance

from
    stg_pp_users as u

left join stg_vp_wallets_collections as cb
    on u.collection_uuid = cb.collection_uuid 
        or u.wallet_address = cb.address