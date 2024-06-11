with raw_users as (
    select
        row_number() OVER () as id,
        user_id,
        total_proposals
    from
        stg_pp_users
),
fake_stg_vp_collection_balances as (
    select
        row_number() OVER () as id,
        collection_id,
        gen_random_uuid() as collection_uuid,
        total_balance
    from
        (
            select
                collection_id,
                gen_random_uuid() as collection_uuid,
                total_balance
            from stg_vp_collection_balances
            order by random()
        )
)

select
    cb.collection_id as collection_id,
    u.user_id,
    u.total_proposals,
    cb.total_balance as balance
from
    raw_users as u
left join fake_stg_vp_collection_balances as cb
    on u.id = cb.id
order by user_id;
