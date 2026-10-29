import csv, sys
B="https://www.sec.gov/Archives/edgar/data/1701605/"
Q = {  # period: (period_end, source, ofse, iet, chart, income statement, reported totals)
"2023-Q1":("2023-03-31",B+"000170160523000047/earningsreleaseex991033120.htm",
  [("Well Construction",1061),("Completions, Intervention & Measurements",909),("Production Solutions",938),("Subsea & Surface Pressure Systems",670)],
  [("Gas Technology Equipment",827),("Gas Technology Services",591),("Condition Monitoring",140),("Inspection",254),("Pumps, Valves & Gears",201),("PSI & Controls",125)],[],
  dict(cost=4567,sga=655,rd=None,restr=56,amort=None,oth_inc=386,oth_exp=None,interest=64,tax=179),dict(ofse=3577,iet=2138,rev=5716,pretax=760,ni=581)),
"2023-Q2":("2023-06-30",B+"000170160523000061/earningsreleaseex991063020.htm",
  [("Well Construction",1076),("Completions, Intervention & Measurements",1090),("Production Solutions",959),("Subsea & Surface Pressure Systems",752)],
  [("Gas Technology Equipment",999),("Gas Technology Services",658),("Condition Monitoring",154),("Inspection",318),("Pumps, Valves & Gears",217),("PSI & Controls",92)],[],
  dict(cost=5004,sga=695,restr=102,oth_inc=158,interest=58,tax=200),dict(ofse=3877,iet=2438,rev=6315,pretax=614,ni=414)),
"2023-Q3":("2023-09-30",B+"000170160523000076/earningsreleaseex991093020.htm",
  [("Well Construction",1128),("Completions, Intervention & Measurements",1085),("Production Solutions",967),("Subsea & Surface Pressure Systems",770)],
  [("Gas Technology Equipment",1254),("Gas Technology Services",637),("Condition Monitoring",157),("Inspection",322),("Pumps, Valves & Gears",232),("PSI & Controls",88)],[],
  dict(cost=5298,sga=627,restr=2,oth_inc=94,interest=49,tax=235),dict(ofse=3951,iet=2691,rev=6641,pretax=759,ni=524)),
"2023-Q4":("2023-12-31",B+"000170160524000007/earningsreleaseex991123120.htm",
  [("Well Construction",1122),("Completions, Intervention & Measurements",1086),("Production Solutions",990),("Subsea & Surface Pressure Systems",758)],
  [("Gas Technology Equipment",1206),("Gas Technology Services",714),("Industrial Products",513),("Industrial Solutions",276),("Climate Technology Solutions",170)],[],
  dict(cost=5386,sga=634,restr=163,oth_inc=-84,interest=45,tax=72),dict(ofse=3956,iet=2879,rev=6835,pretax=522,ni=450)),
"2024-Q1":("2024-03-31",B+"000170160524000065/earningsreleaseex991033120.htm",
  [("Well Construction",1061),("Completions, Intervention & Measurements",1006),("Production Solutions",945),("Subsea & Surface Pressure Systems",771)],
  [("Gas Technology Equipment",1210),("Gas Technology Services",614),("Industrial Products",462),("Industrial Solutions",265),("Climate Technology Solutions",83)],[],
  dict(cost=5140,sga=618,restr=7,oth_inc=29,interest=41,tax=178),dict(ofse=3783,iet=2634,rev=6418,pretax=641,ni=463)),
"2024-Q2":("2024-06-30",B+"000170160524000109/earningsreleaseex991063020.htm",
  [("Well Construction",1090),("Completions, Intervention & Measurements",1118),("Production Solutions",958),("Subsea & Surface Pressure Systems",845)],
  [("Gas Technology Equipment",1539),("Gas Technology Services",691),("Industrial Products",509),("Industrial Solutions",262),("Climate Technology Solutions",128)],[],
  dict(cost=5649,sga=643,restr=14,oth_inc=38,interest=47,tax=243),dict(ofse=4011,iet=3128,rev=7139,pretax=824,ni=581)),
"2024-Q3":("2024-09-30",B+"000170160524000129/earningsreleaseex991093020.htm",
  [("Well Construction",1050),("Completions, Intervention & Measurements",1009),("Production Solutions",983),("Subsea & Surface Pressure Systems",921)],
  [("Gas Technology Equipment",1281),("Gas Technology Services",697),("Industrial Products",520),("Industrial Solutions",257),("Climate Technology Solutions",191)],[],
  dict(cost=5366,sga=612,restr=0,oth_inc=134,interest=55,tax=235),dict(ofse=3963,iet=2945,rev=6908,pretax=1009,ni=774)),
"2024-Q4":("2024-12-31",B+"000170160525000014/earningsreleaseex991123120.htm",
  [("Well Construction",943),("Completions, Intervention & Measurements",1022),("Production Solutions",974),("Subsea & Surface Pressure Systems",932)],
  [("Gas Technology Equipment",1663),("Gas Technology Services",796),("Industrial Products",548),("Industrial Solutions",282),("Climate Technology Solutions",204)],[],
  dict(cost=5833,sga=585,restr=281,oth_inc=181,interest=54,tax=-398),dict(ofse=3871,iet=3492,rev=7364,pretax=792,ni=1190)),
"2025-Q1":("2025-03-31",B+"000170160525000073/earningsreleaseex991033120.htm",
  [("Well Construction",892),("Completions, Intervention & Measurements",925),("Production Solutions",899),("Subsea & Surface Pressure Systems",782)],
  [("Gas Technology Equipment",1456),("Gas Technology Services",592),("Industrial Products",445),("Industrial Solutions",258),("Climate Technology Solutions",178)],[],
  dict(cost=4952,sga=577,rd=146,oth_exp=140,interest=51,tax=152),dict(ofse=3499,iet=2928,rev=6427,pretax=561,ni=409)),
"2025-Q2":("2025-06-30",B+"000170160525000104/earningsreleaseex991063020.htm",
  [("Well Construction",921),("Completions, Intervention & Measurements",935),("Production Solutions",968),("Subsea & Surface Pressure Systems",793)],
  [("Gas Technology Equipment",1624),("Gas Technology Services",752),("Industrial Products",488),("Industrial Solutions",273),("Climate Technology Solutions",156)],[],
  dict(cost=5295,sga=567,rd=161,oth_exp=-134,interest=54,tax=256),dict(ofse=3617,iet=3293,rev=6910,pretax=967,ni=711)),
"2025-Q3":("2025-09-30",B+"000170160525000114/earningsreleaseex991093020.htm",
  [("Well Construction",954),("Completions, Intervention & Measurements",945),("Production Solutions",966),("Subsea & Surface Pressure Systems",771)],
  [("Gas Technology Equipment",1687),("Gas Technology Services",803),("Industrial Products",511),("Industrial Solutions",288),("Climate Technology Solutions",84)],[],
  dict(cost=5309,sga=607,rd=146,oth_exp=71,interest=56,tax=204),dict(ofse=3636,iet=3374,rev=7010,pretax=821,ni=617)),
"2025-Q4":("2025-12-31",B+"000170160526000003/earningsreleaseex991123120.htm",
  [("Well Construction",880),("Completions, Intervention & Measurements",944),("Production Solutions",973),("Subsea & Surface Pressure Systems",775)],
  [("Gas Technology Equipment",1852),("Gas Technology Services",881),("Industrial Products",547),("Industrial Solutions",304),("Climate Technology Solutions",229)],[],
  dict(cost=5633,sga=636,rd=147,restr=215,oth_exp=166,interest=61,tax=-359),dict(ofse=3572,iet=3814,rev=7386,pretax=528,ni=887)),
"2026-Q1":("2026-03-31",B+"000170160526000012/earningsreleaseex991033120.htm",
  [("Well Construction",843),("Completions, Intervention & Measurements",883),("Production Solutions",898),("Subsea & Surface Pressure Systems",613)],
  [("Gas Technology Equipment",1665),("Gas Technology Services",791),("Industrial Products",491),("Industrial Solutions",185),("Climate Technology Solutions",218)],[],
  dict(cost=5083,sga=562,rd=133,restr=37,oth_exp=-588,interest=86,tax=336),dict(ofse=3237,iet=3350,rev=6587,pretax=1274,ni=938)),
"2026-Q2":("2026-06-30",B+"000170160526000021/earningsreleaseex991063020.htm",
  [("Well Construction",899),("Completions, Intervention & Measurements",944),("Production Solutions",930),("Subsea & Surface Pressure Systems",678)],
  [("Gas Technology Equipment",1524),("Gas Technology Services",831),("Industrial Products",549),("Industrial Solutions",182),("Climate Technology Solutions",205)],[],
  dict(cost=5165,sga=569,rd=143,restr=11,oth_exp=-104,interest=66,tax=210),dict(ofse=3451,iet=3291,rev=6742,pretax=892,ni=682)),
"2026-Q3":("2026-09-30",B+"000170160526000033/earningsreleaseex991093020.htm",
  [("Well Construction",958),("Completions, Intervention & Measurements",1008),("Production Solutions",983),("Subsea & Surface Pressure Systems",711)],
  [("Gas Technology Equipment",1576),("Gas Technology Services",897),("Industrial Products",537),("Industrial Solutions",205),("Climate Technology Solutions",262)],
  [("Original Equipment",623),("Aftermarket",265)],
  dict(cost=6097,sga=732,rd=150,restr=28,amort=165,oth_exp=157,interest=177,tax=97),dict(ofse=3660,iet=3477,chart=888,rev=8025,pretax=519,ni=422)),
}
IS = [  # key, label, pl_sign (+ adds to net income, - reduces it)
 ("cost","Cost of revenue",-1),("sga","Selling, general and administrative",-1),("rd","Research and development",-1),
 ("restr","Restructuring, impairment and other",-1),("amort","Amortization of acquired intangible assets",-1),
 ("oth_inc","Other non-operating income (loss), net",+1),("oth_exp","Other (income) expense, net",-1),
 ("interest","Interest expense, net",-1),("tax","Provision (benefit) for income taxes",-1)]
rows=[]; bad=0
for p,(end,src,ofse,iet,chart,ist,tot) in Q.items():
    def add(lt,seg,lab,amt,sign): rows.append(dict(fiscal_period=p,period_end=end,line_type=lt,segment=seg,line_label=lab,amount_usd_m=amt,pl_sign=sign,source_url=src))
    for seg,lines in (("OFSE",ofse),("IET",iet),("Chart",chart)):
        for lab,a in lines: add("revenue","%s"%seg,lab,a,1)
    pnl=sum(a for _,a in ofse+iet+chart)
    for k,lab,s in IS:
        if ist.get(k) is not None:
            v=ist[k]; lab2=lab
            if k=="restr" and p>="2025": lab2="Restructuring"
            add("expense_or_other","Total",lab2,v,s); pnl+=s*v
    for k,lab in (("ofse","Total OFSE revenue"),("iet","Total IET revenue"),("chart","Total Chart revenue"),("rev","Total revenue"),("pretax","Income before income taxes"),("ni","Net income")):
        if k in tot: add("reported_total","Total",lab,tot[k],0)
    # checks
    seg_chk=[(n,sum(a for _,a in l),tot.get(k)) for n,l,k in (("OFSE",ofse,"ofse"),("IET",iet,"iet"),("Chart",chart,"chart")) if l]
    revsum=sum(t for _,_,t in seg_chk)
    pre=tot["rev"]-sum(ist.get(k) or 0 for k in("cost","sga","rd","restr","amort","oth_exp","interest"))+(ist.get("oth_inc") or 0)
    msgs=[f"{n} lines {s} vs {t} ({s-t:+d})" for n,s,t in seg_chk if s!=t]
    if revsum!=tot["rev"]: msgs.append(f"segments {revsum} vs rev {tot['rev']}")
    if pre!=tot["pretax"]: msgs.append(f"pretax {pre} vs {tot['pretax']}")
    if pre-ist["tax"]!=tot["ni"]: msgs.append(f"NI {pre-ist['tax']} vs {tot['ni']}")
    print(p, "OK" if not msgs else "; ".join(msgs)); bad+=bool(msgs)
with open(sys.argv[1],"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
print(len(rows),"rows; quarters with issues:",bad)
