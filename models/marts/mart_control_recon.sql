-- Reconciles synthetic GL detail to Baker Hughes reported results, one row per quarter x P&L line.
-- gap_usd = amount booked in the GL minus amount reported; +/- $1M tolerance covers rounding in the earnings release.
with gl as (
    select
        g.period                                        as fiscal_period,
        c.control_line_label                            as line_label,
        sum(g.credit_amount_usd - g.debit_amount_usd)   as gl_pl_impact_usd,
        count(distinct g.journal_entry_id)              as journal_entry_count
    from {{ ref('stg_gl_entries') }} g
    join {{ ref('stg_chart_of_accounts') }} c
      on g.account_code = c.account_code
    where coalesce(c.control_line_label, '') <> ''
    group by 1, 2
),

ctl as (
    select * from {{ ref('stg_control_totals') }}
    where pl_sign <> 0
),

joined as (
    select
        ctl.fiscal_period,
        ctl.period_end,
        ctl.line_type,
        ctl.segment,
        ctl.line_label,
        ctl.amount_usd_m * 1000000                         as reported_usd,
        coalesce(gl.gl_pl_impact_usd, 0) * ctl.pl_sign     as booked_usd,
        coalesce(gl.journal_entry_count, 0)                as journal_entry_count,
        ctl.source_url
    from ctl
    left join gl
      on gl.fiscal_period = ctl.fiscal_period
     and gl.line_label    = ctl.line_label
)

select
    *,
    booked_usd - reported_usd as gap_usd,
    case
        when abs(booked_usd - reported_usd) <= 1000000 then 'TIED'
        when booked_usd > reported_usd                 then 'OVER'
        else 'UNDER'
    end as recon_status
from joined
