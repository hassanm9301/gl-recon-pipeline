-- Double-entry check: every journal entry's debits must equal its credits.
-- Returns the entries that don't balance; the test passes when no rows come back.
select
    journal_entry_id,
    sum(debit_amount_usd)  as total_debits,
    sum(credit_amount_usd) as total_credits
from {{ ref('fct_gl_entries') }}
group by journal_entry_id
having abs(sum(debit_amount_usd) - sum(credit_amount_usd)) > 0.005
