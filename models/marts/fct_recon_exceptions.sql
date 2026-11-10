-- Points each OVER/UNDER line in mart_control_recon to the journal entries that cause it.
-- Exceptions are classified from the data structure only (dates, accounts, amounts);
-- the free-text description is never parsed.
with lines as (
    select
        g.*,
        c.control_line_label,
        g.debit_amount_usd + g.credit_amount_usd as amount_usd,
        -- quarter the transaction date falls in, in the same format as period (e.g. 2025-Q4)
        cast(g.fiscal_year as varchar) || '-Q' || cast(g.fiscal_quarter as varchar) as date_period,
        -- revenue posted by an entity that is not expected to book that revenue account
        case when c.category = 'Revenue' and m.account_code is null then 1 else 0 end as unexpected_account,
        count(*) over (
            partition by g.account_code, g.entity_id, g.entry_date, g.debit_amount_usd, g.credit_amount_usd
        ) as same_posting_count
    from {{ ref('fct_gl_entries') }} g
    join {{ ref('stg_chart_of_accounts') }} c
      on g.account_code = c.account_code
    left join {{ ref('stg_entity_revenue_accounts') }} m
      on m.entity_id    = g.entity_id
     and m.account_code = g.account_code
    where coalesce(c.control_line_label, '') <> ''
),

breaks as (
    select * from {{ ref('mart_control_recon') }}
    where recon_status <> 'TIED'
),

-- entries whose amount equals the gap on a broken line
matched as (
    select
        case
            when l.date_period <> l.period   then 'cutoff_error'     -- dated in one quarter, posted to another
            when l.unexpected_account = 1    then 'wrong_account'    -- entity/account pair outside the mapping
            when l.same_posting_count > 1    then 'duplicate_entry'  -- same account, entity, date and amount twice
            else 'unexplained'
        end                     as exception_type,
        b.fiscal_period,
        b.line_label,
        b.recon_status,
        b.gap_usd,
        l.journal_entry_id,
        l.entry_date,
        l.account_code,
        l.entity_id,
        l.amount_usd,
        l.description
    from breaks b
    join lines l
      on l.period             = b.fiscal_period
     and l.control_line_label = b.line_label
     and abs(l.amount_usd - abs(b.gap_usd)) <= 1
),

-- gaps in journal entry numbering (numbering restarts each quarter)
je_numbers as (
    select distinct
        journal_entry_id,
        substr(journal_entry_id, 4, 7)                    as je_period,
        cast(substr(journal_entry_id, 12, 4) as integer)  as je_number
    from {{ ref('fct_gl_entries') }}
),

numbering_gaps as (
    select
        je_period,
        lag(je_number) over (partition by je_period order by je_number) as prev_number,
        je_number
    from je_numbers
),

missing as (
    select
        'missing_entry'                                   as exception_type,
        je_period                                         as fiscal_period,
        cast(null as varchar)                             as line_label,
        cast(null as varchar)                             as recon_status,
        cast(null as numeric(18, 2))                      as gap_usd,
        'JE-' || je_period || '-' || lpad(cast(prev_number + 1 as varchar), 4, '0') as journal_entry_id,
        cast(null as date)                                as entry_date,
        cast(null as varchar)                             as account_code,
        cast(null as varchar)                             as entity_id,
        cast(null as bigint)                              as amount_usd,
        'Journal entry number skipped; check UNDER lines in this quarter' as description
    from numbering_gaps
    where je_number - prev_number > 1
)

select * from matched
union all
select * from missing
