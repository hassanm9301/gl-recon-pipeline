"""Generate synthetic GL detail that ties to seeds/control_totals.csv.

Writes seeds/chart_of_accounts.csv, seeds/entities.csv and seeds/gl_entries.csv.
- Every P&L line in control_totals (pl_sign != 0) gets synthetic double-entry journal
  entries dated inside the real quarter, summing exactly to the reported amount.
- Four planted breaks are applied afterwards (listed in PLANTED_BREAKS and the README).
Standard library only; fixed random seed so output is reproducible:  python scripts/make_gl_entries.py
"""
import csv, random, datetime as dt
from pathlib import Path

SEED = 42
ROOT = Path(__file__).resolve().parent.parent
SEEDS = ROOT / "seeds"
rng = random.Random(SEED)

# ---- reference data ---------------------------------------------------------
ENTITIES = [
    ("BKR-CORP", "Baker Hughes Company", "Parent", "Corporate", "Global", "USA"),
    ("BKR-OFSE-NA", "BKR Oilfield Services NA", "Operating", "OFSE", "North America", "USA"),
    ("BKR-OFSE-INTL", "BKR Oilfield Services International", "Operating", "OFSE", "International", "Multiple"),
    ("BKR-OFSE-SUBSEA", "BKR Subsea and Surface Systems", "Operating", "OFSE", "Global", "Multiple"),
    ("BKR-IET-GTE", "BKR Gas Technology Equipment", "Operating", "IET", "Global", "Multiple"),
    ("BKR-IET-GTS", "BKR Gas Technology Services", "Operating", "IET", "Global", "Multiple"),
    ("BKR-IET-IP", "BKR Industrial Products", "Operating", "IET", "Global", "Multiple"),
    ("BKR-IET-IS", "BKR Industrial Solutions", "Operating", "IET", "Global", "Multiple"),
    ("BKR-IET-CTS", "BKR Climate Technology Solutions", "Operating", "IET", "Global", "Multiple"),
    ("BKR-CHART", "Chart Industries", "Operating", "Chart", "Global", "Multiple"),
]

# account_code, account_name, account_type, category, segment, control_line_label (blank = balance sheet)
COA = [
    ("1000", "Cash and Cash Equivalents", "Asset", "Current Asset", "Corporate", ""),
    ("1100", "Accounts Receivable", "Asset", "Current Asset", "Corporate", ""),
    ("2000", "Accounts Payable", "Liability", "Current Liability", "Corporate", ""),
    ("2100", "Accrued Expenses", "Liability", "Current Liability", "Corporate", ""),
    ("2300", "Income Taxes Payable", "Liability", "Current Liability", "Corporate", ""),
    ("4000", "Revenue - Well Construction", "Revenue", "Revenue", "OFSE", "Well Construction"),
    ("4010", "Revenue - Completions, Intervention & Measurements", "Revenue", "Revenue", "OFSE", "Completions, Intervention & Measurements"),
    ("4020", "Revenue - Production Solutions", "Revenue", "Revenue", "OFSE", "Production Solutions"),
    ("4030", "Revenue - Subsea & Surface Pressure Systems", "Revenue", "Revenue", "OFSE", "Subsea & Surface Pressure Systems"),
    ("4100", "Revenue - Gas Technology Equipment", "Revenue", "Revenue", "IET", "Gas Technology Equipment"),
    ("4110", "Revenue - Gas Technology Services", "Revenue", "Revenue", "IET", "Gas Technology Services"),
    ("4120", "Revenue - Industrial Products", "Revenue", "Revenue", "IET", "Industrial Products"),
    ("4130", "Revenue - Industrial Solutions", "Revenue", "Revenue", "IET", "Industrial Solutions"),
    ("4140", "Revenue - Climate Technology Solutions", "Revenue", "Revenue", "IET", "Climate Technology Solutions"),
    ("4150", "Revenue - Condition Monitoring (pre-2023-Q4)", "Revenue", "Revenue", "IET", "Condition Monitoring"),
    ("4160", "Revenue - Inspection (pre-2023-Q4)", "Revenue", "Revenue", "IET", "Inspection"),
    ("4170", "Revenue - Pumps, Valves & Gears (pre-2023-Q4)", "Revenue", "Revenue", "IET", "Pumps, Valves & Gears"),
    ("4180", "Revenue - PSI & Controls (pre-2023-Q4)", "Revenue", "Revenue", "IET", "PSI & Controls"),
    ("4200", "Revenue - Chart Original Equipment", "Revenue", "Revenue", "Chart", "Original Equipment"),
    ("4210", "Revenue - Chart Aftermarket", "Revenue", "Revenue", "Chart", "Aftermarket"),
    ("5000", "Cost of Revenue", "Expense", "COGS", "Corporate", "Cost of revenue"),
    ("6000", "Research and Development", "Expense", "Operating Expense", "Corporate", "Research and development"),
    ("6100", "Selling, General and Administrative", "Expense", "Operating Expense", "Corporate", "Selling, general and administrative"),
    ("6300", "Restructuring, Impairment and Other", "Expense", "Operating Expense", "Corporate", "Restructuring, impairment and other"),
    ("6310", "Restructuring", "Expense", "Operating Expense", "Corporate", "Restructuring"),
    ("6400", "Amortization of Acquired Intangible Assets", "Expense", "Operating Expense", "Corporate", "Amortization of acquired intangible assets"),
    ("7000", "Interest Expense, Net", "Expense", "Non-Operating", "Corporate", "Interest expense, net"),
    ("7100", "Other Non-Operating Income (Loss), Net", "Revenue", "Non-Operating", "Corporate", "Other non-operating income (loss), net"),
    ("7110", "Other (Income) Expense, Net", "Expense", "Non-Operating", "Corporate", "Other (income) expense, net"),
    ("8000", "Provision (Benefit) for Income Taxes", "Expense", "Tax", "Corporate", "Provision (benefit) for income taxes"),
]
ACCT = {r[5]: r for r in COA if r[5]}

# entity choices per control line
LINE_ENTITIES = {
    "Well Construction": ["BKR-OFSE-NA", "BKR-OFSE-INTL"],
    "Completions, Intervention & Measurements": ["BKR-OFSE-NA", "BKR-OFSE-INTL"],
    "Production Solutions": ["BKR-OFSE-NA", "BKR-OFSE-INTL"],
    "Subsea & Surface Pressure Systems": ["BKR-OFSE-SUBSEA"],
    "Gas Technology Equipment": ["BKR-IET-GTE"],
    "Gas Technology Services": ["BKR-IET-GTS"],
    "Industrial Products": ["BKR-IET-IP"], "Condition Monitoring": ["BKR-IET-IP"], "Inspection": ["BKR-IET-IP"],
    "Industrial Solutions": ["BKR-IET-IS"], "Pumps, Valves & Gears": ["BKR-IET-IS"], "PSI & Controls": ["BKR-IET-IS"],
    "Climate Technology Solutions": ["BKR-IET-CTS"],
    "Original Equipment": ["BKR-CHART"], "Aftermarket": ["BKR-CHART"],
}
OPERATING = [e[0] for e in ENTITIES if e[2] == "Operating"]
SEGMENT_OF = {e[0]: e[3] for e in ENTITIES}

# entries per control line per quarter (~500 entries / quarter)
N_ENTRIES = {"revenue": 40, "Cost of revenue": 60, "Selling, general and administrative": 30, "Research and development": 12}
DEFAULT_N = 8

def offset_account(line_label, credit_pl):
    """Balance-sheet side of the entry."""
    if ACCT[line_label][2] == "Revenue" and ACCT[line_label][3] == "Revenue":
        return "1100"                       # revenue -> AR
    if line_label == "Provision (benefit) for income taxes":
        return "2300"
    if line_label == "Interest expense, net" or ACCT[line_label][3] == "Non-Operating":
        return "1000"
    return "2100" if not credit_pl else "2100"   # accrued expenses (or reversal)

def split(total, n):
    """Split a positive integer total into n positive integers that sum exactly to total."""
    n = max(1, min(n, total))
    weights = [rng.uniform(0.3, 1.7) for _ in range(n)]
    s = sum(weights)
    parts = [max(1, int(total * w / s)) for w in weights]
    parts[-1] += total - sum(parts)
    return parts

def weekday_in_quarter(period_end):
    end = dt.date.fromisoformat(period_end)
    start = (end.replace(day=1) - dt.timedelta(days=62)).replace(day=1)
    while True:
        d = start + dt.timedelta(days=rng.randint(0, (end - start).days))
        if d.weekday() < 5:
            return d

# ---- build entries ------------------------------------------------------------
controls = list(csv.DictReader(open(SEEDS / "control_totals.csv", newline="", encoding="utf-8")))
entries = []        # dicts, one per journal entry (two GL lines each)
seq = {}
for c in controls:
    sign = int(c["pl_sign"])
    if sign == 0:
        continue
    label, period = c["line_label"], c["fiscal_period"]
    amount = round(float(c["amount_usd_m"]) * 1_000_000)
    if amount == 0:
        continue
    impact = sign * amount                       # >0 increases income, <0 decreases
    credit_pl = impact > 0
    n = N_ENTRIES.get("revenue" if c["line_type"] == "revenue" else label, DEFAULT_N)
    for part in split(abs(amount), n):
        ent = rng.choice(LINE_ENTITIES.get(label, OPERATING if label in N_ENTRIES else ["BKR-CORP"]))
        seq[period] = seq.get(period, 0) + 1
        entries.append(dict(
            je=f"JE-{period}-{seq[period]:04d}", date=weekday_in_quarter(c["period_end"]), period=period,
            pl_acct=ACCT[label][0], off_acct=offset_account(label, credit_pl), entity=ent,
            amount=part, credit_pl=credit_pl, label=label,
            entry_type=ACCT[label][2], desc=f"{label} - {period}"))

# ---- planted breaks (each > $1M so it breaks the +/- $1M tolerance) --------------
def biggest(period, label):
    return max((e for e in entries if e["period"] == period and e["label"] == label), key=lambda e: e["amount"])

PLANTED_BREAKS = []
# 1. Duplicate entry: same entry posted twice -> line OVER
dup = dict(biggest("2024-Q2", "Well Construction"))
seq["2024-Q2"] += 1
dup["je"] = f"JE-2024-Q2-{seq['2024-Q2']:04d}"
dup["desc"] += " (duplicate)"
entries.append(dup)
PLANTED_BREAKS.append(("duplicate_entry", dup["je"], "2024-Q2 Well Construction OVER by $" + f"{dup['amount']:,}"))
# 2. Cut-off error: Q4 entry booked in the next quarter -> 2025-Q4 UNDER, 2026-Q1 OVER
cut = biggest("2025-Q4", "Gas Technology Equipment")
cut["date"], cut["period"] = dt.date(2026, 1, 2), "2026-Q1"
PLANTED_BREAKS.append(("cutoff_error", cut["je"], "2025-Q4 Gas Technology Equipment UNDER / 2026-Q1 OVER by $" + f"{cut['amount']:,}"))
# 3. Wrong account: Production Solutions revenue posted to Subsea account
wrong = biggest("2024-Q3", "Production Solutions")
wrong["pl_acct"] = ACCT["Subsea & Surface Pressure Systems"][0]
PLANTED_BREAKS.append(("wrong_account", wrong["je"], "2024-Q3 Production Solutions UNDER / Subsea OVER by $" + f"{wrong['amount']:,}"))
# 4. Missing entry: an SG&A accrual never booked -> SG&A UNDER (prints as a gap in JE numbering)
miss = biggest("2023-Q2", "Selling, general and administrative")
entries.remove(miss)
PLANTED_BREAKS.append(("missing_entry", miss["je"], "2023-Q2 SG&A UNDER by $" + f"{miss['amount']:,}"))

# ---- write seeds ----------------------------------------------------------------
with open(SEEDS / "entities.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["entity_id", "entity_name", "entity_type", "segment", "region", "country"]); w.writerows(ENTITIES)
with open(SEEDS / "chart_of_accounts.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["account_code", "account_name", "account_type", "category", "segment", "control_line_label"]); w.writerows(COA)

names = {r[0]: r[1] for r in COA}
entries.sort(key=lambda e: (e["period"], e["je"]))
with open(SEEDS / "gl_entries.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["gl_line_id", "journal_entry_id", "line_number", "entry_date", "period", "account_code", "account_name",
                "entity_id", "debit_amount_usd", "credit_amount_usd", "description", "entry_type", "segment"])
    for e in entries:
        seg = SEGMENT_OF[e["entity"]] if e["entity"] != "BKR-CORP" else "Corporate"
        pl = (e["pl_acct"], 0, e["amount"]) if e["credit_pl"] else (e["pl_acct"], e["amount"], 0)
        bs = (e["off_acct"], e["amount"], 0) if e["credit_pl"] else (e["off_acct"], 0, e["amount"])
        for i, (acct, dr, cr) in enumerate((pl, bs), start=1):
            w.writerow([f"{e['je']}-{i}", e["je"], i, e["date"].isoformat(), e["period"], acct, names[acct],
                        e["entity"], dr, cr, e["desc"], e["entry_type"], seg])

print(f"{len(entries)} journal entries, {2 * len(entries)} GL lines")
for b in PLANTED_BREAKS:
    print("planted:", *b)
