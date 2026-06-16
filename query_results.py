import duckdb

con = duckdb.connect(r'C:\Users\hassa\gl_recon_pipeline\gl_recon\gl_recon.duckdb')

print("\n=== GL Reconciliation - Segment Summary ===")
print(con.execute("""
    select 
        period,
        segment,
        round(total_debits/1e6, 2)  as debits_millions,
        round(total_credits/1e6, 2) as credits_millions,
        round(net_amount/1e6, 2)    as net_millions,
        balance_check
    from mart_gl_reconciliation
    where segment != 'Corporate'
    order by period, segment
""").df().to_string())

con.close()