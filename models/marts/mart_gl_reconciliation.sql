with gl as (
    select * from {{ ref('fct_gl_entries') }}
),

coa as (
    select * from {{ ref('stg_chart_of_accounts') }}
),

joined as (
    select
        gl.journal_entry_id,
        gl.entry_date,
        gl.period,
        gl.fiscal_year,
        gl.fiscal_quarter,
        gl.segment,
        gl.entity_id,
        gl.account_code,
        coa.account_name,
        coa.account_type,
        coa.category,
        gl.entry_type,
        gl.description,
        gl.debit_amount_usd,
        gl.credit_amount_usd,
        gl.net_amount_usd
    from gl
    left join coa on gl.account_code = coa.account_code
),

reconciled as (
    select
        period,
        fiscal_year,
        fiscal_quarter,
        segment,
        account_type,
        category,
        sum(debit_amount_usd)               as total_debits,
        sum(credit_amount_usd)              as total_credits,
        sum(net_amount_usd)                 as net_amount,
        count(journal_entry_id)             as entry_count,
        sum(debit_amount_usd) - sum(credit_amount_usd) as balance_check
    from joined
    group by
        period,
        fiscal_year,
        fiscal_quarter,
        segment,
        account_type,
        category
)

select * from reconciled