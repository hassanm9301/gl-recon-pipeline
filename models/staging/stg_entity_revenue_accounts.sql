-- Which entities are expected to book each revenue account. A revenue posting outside this
-- mapping is flagged as a wrong-account exception.
select
    entity_id,
    account_code
from {{ ref('entity_revenue_accounts') }}
