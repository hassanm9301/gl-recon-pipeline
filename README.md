# GL Reconciliation Pipeline — Baker Hughes (BKR)

![dbt](https://img.shields.io/badge/dbt-FF694B?style=flat&logo=dbt&logoColor=white)
![Snowflake](https://img.shields.io/badge/Snowflake-29B5E8?style=flat&logo=snowflake&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-FFF000?style=flat&logo=duckdb&logoColor=black)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-4479A1?style=flat&logo=mysql&logoColor=white)

## Overview

An end-to-end GL reconciliation pipeline built with dbt Core. The same project runs on two
targets: **DuckDB** locally and **Snowflake** in the cloud. It is modeled on Baker Hughes
Company's FY2023 Annual Report (Form 10-K, SEC EDGAR).

The pipeline automates what GL accountants do by hand: reconciling debits and credits across
business segments, validating data quality, and producing audit-ready output.

---

## Business Context

Baker Hughes (NASDAQ: BKR) is a Houston-based energy technology company with two operating
segments:

| Segment | Full Name | FY2023 Revenue |
|---|---|---|
| OFSE | Oilfield Services & Equipment | $15.4B |
| IET | Industrial & Energy Technology | $10.1B |
| **Total** | | **$25.5B** |

---

## Pipeline Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        RAW DATA (seeds)                      │
│  gl_entries.csv   │  chart_of_accounts.csv  │  entities.csv  │
│  (81 rows)        │  (36 rows)              │  (8 rows)      │
└──────────────────────────────┬───────────────────────────────┘
                               │ dbt seed
                               ▼
┌──────────────────────────────────────────────────────────────┐
│           WAREHOUSE: DuckDB (local) or Snowflake             │
│     gl_recon.duckdb      │      GL_RECON.DEV (Snowflake)     │
└──────────────────────────────┬───────────────────────────────┘
                               │ dbt run
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                    STAGING LAYER (views)                     │
│   stg_gl_entries               │   stg_chart_of_accounts     │
│   - Clean and type dates       │   - Account reference       │
│   - Add fiscal_year / quarter  │   - Account types           │
└──────────────────────────────┬───────────────────────────────┘
                               │ join + group by
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                     MARTS LAYER (table)                      │
│                   mart_gl_reconciliation                     │
│   - Segment breakdown (OFSE vs IET)                          │
│   - Quarterly P&L summary                                    │
│   - Debit/credit balance check                               │
│   - Automated data quality tests (8/8 PASS)                  │
└──────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Tool | Purpose |
|---|---|
| dbt Core | Data transformation, modeling, and testing |
| Snowflake | Cloud data warehouse target |
| DuckDB | Local analytical database target |
| Python | Querying and result output |
| SQL | Business logic and transformations |
| Git + GitHub | Version control |

---

## Models

| Model | Layer | Type | Description |
|---|---|---|---|
| `stg_gl_entries` | Staging | View | Cleaned and typed GL journal entries |
| `stg_chart_of_accounts` | Staging | View | Account reference data |
| `mart_gl_reconciliation` | Marts | Table | Final reconciliation by segment and period |

---

## Data Tests

| Test | Column | Result |
|---|---|---|
| unique | journal_entry_id | ✅ PASS |
| not_null | journal_entry_id | ✅ PASS |
| not_null | entry_date | ✅ PASS |
| not_null | account_code | ✅ PASS |
| not_null | segment | ✅ PASS |
| accepted_values | segment | ✅ PASS |
| unique | account_code (COA) | ✅ PASS |
| not_null | account_code (COA) | ✅ PASS |

**8/8 tests passing on both DuckDB and Snowflake.**

---

## Key Metrics (FY2023)

- Total Revenue: **$25.5B**
- OFSE Revenue: **$15.4B**
- IET Revenue: **$10.1B**
- Restructuring Charge: **$323M**
- GL Entries Processed: **81**
- Data Quality Tests: **8/8 PASS**

---

## How to Run

### Locally on DuckDB (default target)

```bash
# 1. Activate the virtual environment
venv\Scripts\activate

# 2. Seed, run, and test in one step
dbt build

# 3. Query results
python query_results.py
```

### On Snowflake

```bash
dbt debug --target snowflake   # check the connection (key-pair auth)
dbt build --target snowflake   # seed, run, and test
```

Snowflake setup: warehouse `DBT_WH` (X-Small, 60-second auto-suspend), database `GL_RECON`,
schema `DEV`, role `TRANSFORMER`, and service user `DBT_USER` with key-pair authentication.
Connection details live in `~/.dbt/profiles.yml` and are not committed to this repo.

---

## Data Source

- **Baker Hughes Company Form 10-K**, fiscal year ended December 31, 2023
- Filed with SEC EDGAR on February 5, 2024
- Source: https://www.sec.gov/Archives/edgar/data/0001701605/000170160524000033/bkr-20231231.htm

Segment revenue and the other key metrics above come from the 10-K. The individual journal
entries are synthetic: they were generated so their totals tie to the 10-K figures, which gives
the reconciliation tests real numbers to check against.

---

## Author

**Muhammad Hassan**
GL Programmer → Analytics Engineering
Houston, TX
GitHub: [@hassanm9301](https://github.com/hassanm9301)
