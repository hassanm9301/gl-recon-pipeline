with source as (
    select * from {{ ref('gl_entries') }}
),

cleaned as (
    select
        journal_entry_id,
        cast(entry_date as date)          as entry_date,
        period,
        account_code,
        account_name,
        entity_id,
        debit_amount_usd,
        credit_amount_usd,
        (debit_amount_usd - credit_amount_usd) as net_amount_usd,
        description,
        entry_type,
        segment,
        year(cast(entry_date as date))    as fiscal_year,
        quarter(cast(entry_date as date)) as fiscal_quarter
    from source
)

select * from cleaned