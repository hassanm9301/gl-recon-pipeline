-- Central GL fact table. Incremental: each run reprocesses only recent journal entries
-- instead of rebuilding the whole ledger.
--   * delete+insert on journal_entry_id replaces every line of a re-posted entry together,
--     so an entry can never end up half old, half new.
--   * The 7-day lookback catches entries posted late into an already-loaded period.
-- Run `dbt build --full-refresh` to rebuild from scratch.

{{ config(
    materialized='incremental',
    unique_key='journal_entry_id',
    incremental_strategy='delete+insert',
    on_schema_change='fail'
) }}

select
    gl_line_id,
    journal_entry_id,
    line_number,
    entry_date,
    period,
    fiscal_year,
    fiscal_quarter,
    account_code,
    account_name,
    entity_id,
    segment,
    debit_amount_usd,
    credit_amount_usd,
    net_amount_usd,
    description,
    entry_type
from {{ ref('stg_gl_entries') }}

{% if is_incremental() %}
where entry_date >= (
    select {{ dbt.dateadd('day', -7, 'max(entry_date)') }} from {{ this }}
)
{% endif %}
