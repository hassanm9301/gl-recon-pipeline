with source as (
    select * from {{ ref('chart_of_accounts') }}
),

cleaned as (
    select
        account_code,
        account_name,
        account_type,
        category,
        segment,
        control_line_label
    from source
)

select * from cleaned