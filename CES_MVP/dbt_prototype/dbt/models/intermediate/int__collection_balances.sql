select
    c.collection_id,
    c.collection_uuid,
    count(distinct c.address) as num_wallets,
    -- balance is the sum of balance and stake
    sum(coalesce(a.balance, 0) + coalesce(a.stake, 0)) as balance,
    sum(coalesce(a.balance, 0)) as raw_balance,
    sum(coalesce(a.stake, 0)) as raw_stake,
from
    {{ ref('stg_vp__wallets_collections') }} as c
left join {{ ref('stg_vp__agix_balance_snapshot') }} as a
    on c.address = a.address
group by
    1, 2
