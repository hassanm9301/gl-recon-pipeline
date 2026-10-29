with source as (
    select * from {{ ref('control_totals') }}
)

select
    fiscal_period,
    cast(period_end as date)              as period_end,
    line_type,
    segment,
    line_label,
    cast(amount_usd_m as numeric(18, 2))  as amount_usd_m,
    cast(pl_sign as integer)              as pl_sign,
    source_url
from source
