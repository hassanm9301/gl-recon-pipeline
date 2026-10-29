-- Points each OVER/UNDER line in mart_control_recon to the journal entries that cause it.
with lines as (
    select
        g.*,
        c.control_line_label,
        g.debit_amount_usd + g.credit_amount_usd as amount_usd,
        count(*) over (
            partition by g.account_code, g.entity_id, g.entry_date, g.debit_amount_usd, g.credit_amount_usd
        ) as same_posting_count
    from {{ ref('stg_gl_entries') }} g
    join {{ ref('stg_chart_of_accounts') }} c
      on g.account_code = c.account_code
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
            when split_part(l.description, ' - ', 1) <> l.control_line_label then 'wrong_account'
            when substr(split_part(l.description, ' - ', 2), 1, 7) <> l.period then 'cutoff_error'
            when l.same_posting_count > 1                                     then 'duplicate_entry'
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
    from {{ ref('stg_gl_entries') }}
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
