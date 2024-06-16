select
    c.collection_id,
    c.collection_uuid,
    count(distinct c.address) as num_wallets,
    sum(coalesce(a.balance, 0)) as balance,
from
    stg_vp_wallets_collections as c
left join stg_vp_agix_balance_snapshot as a
    on c.address = a.address
group by
    1, 2
;