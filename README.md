\# GL Reconciliation Pipeline — Baker Hughes (BKR)



!\[dbt](https://img.shields.io/badge/dbt-FF694B?style=flat\&logo=dbt\&logoColor=white)

!\[DuckDB](https://img.shields.io/badge/DuckDB-FFF000?style=flat\&logo=duckdb\&logoColor=black)

!\[Python](https://img.shields.io/badge/Python-3776AB?style=flat\&logo=python\&logoColor=white)

!\[SQL](https://img.shields.io/badge/SQL-4479A1?style=flat\&logo=mysql\&logoColor=white)



\## Overview

An end-to-end GL reconciliation pipeline built using dbt Core and DuckDB, 

powered by real financial data from Baker Hughes Company's 2023 Annual Report (10-K filed with SEC EDGAR).



This project automates what GL accountants do manually — reconciling debits and credits 

across business segments, validating data quality, and producing audit-ready output.



\---



\## Business Context

Baker Hughes (NASDAQ: BKR) is a Houston-based energy technology company with 

two operating segments:



| Segment | Full Name | FY2023 Revenue |

|---|---|---|

| OFSE | Oilfield Services \& Equipment | $15.4B |

| IET | Industrial \& Energy Technology | $10.1B |

| \*\*Total\*\* | | \*\*$25.5B\*\* |



\---



\## Pipeline Architecture



```

┌─────────────────────────────────────────────────────┐

│                   RAW DATA LAYER                    │

│  gl\_entries.csv  │  chart\_of\_accounts.csv  │  entities.csv  │

│  (81 rows)       │  (36 rows)              │  (8 rows)      │

└────────────────────────┬────────────────────────────┘

&#x20;                        │ dbt seed

&#x20;                        ▼

┌─────────────────────────────────────────────────────┐

│                    DUCKDB                           │

│              gl\_recon.duckdb                        │

└────────────────────────┬────────────────────────────┘

&#x20;                        │ dbt run

&#x20;                        ▼

┌─────────────────────────────────────────────────────┐

│                 STAGING LAYER (Views)               │

│   stg\_gl\_entries      │   stg\_chart\_of\_accounts     │

│   - Clean dates       │   - Account reference       │

│   - Add fiscal\_year   │   - Account types           │

│   - Add fiscal\_qtr    │                             │

└────────────────────────┬────────────────────────────┘

&#x20;                        │ JOIN + GROUP BY

&#x20;                        ▼

┌─────────────────────────────────────────────────────┐

│                  MARTS LAYER (Table)                │

│             mart\_gl\_reconciliation                  │

│   - Segment breakdown (OFSE vs IET)                 │

│   - Quarterly P\&L summary                          │

│   - Debit/Credit balance check                      │

│   - Automated data quality tests (8/8 PASS)         │

└─────────────────────────────────────────────────────┘

```



\---



\## Tech Stack



| Tool | Purpose |

|---|---|

| dbt Core | Data transformation and modeling |

| DuckDB | Local analytical database |

| Python | Querying and result output |

| SQL | Business logic and transformations |

| Git + GitHub | Version control |



\---



\## Models



| Model | Layer | Type | Description |

|---|---|---|---|

| `stg\_gl\_entries` | Staging | View | Cleaned and typed GL journal entries |

| `stg\_chart\_of\_accounts` | Staging | View | Account reference data |

| `mart\_gl\_reconciliation` | Marts | Table | Final reconciliation by segment and period |



\---



\## Data Tests



| Test | Column | Result |

|---|---|---|

| unique | journal\_entry\_id | ✅ PASS |

| not\_null | journal\_entry\_id | ✅ PASS |

| not\_null | entry\_date | ✅ PASS |

| not\_null | account\_code | ✅ PASS |

| not\_null | segment | ✅ PASS |

| accepted\_values | segment | ✅ PASS |

| unique | account\_code (COA) | ✅ PASS |

| not\_null | account\_code (COA) | ✅ PASS |



\*\*8/8 tests passing\*\*



\---



\## Key Metrics (FY2023)



\- Total Revenue: \*\*$25.5B\*\*

\- OFSE Revenue: \*\*$15.4B\*\*

\- IET Revenue: \*\*$10.1B\*\*

\- Restructuring Charge: \*\*$323M\*\*

\- Total GL Entries Processed: \*\*81\*\*

\- Data Quality Tests: \*\*8/8 PASS\*\*



\---



\## How to Run



```bash

\# 1. Activate virtual environment

venv\\Scripts\\activate



\# 2. Load raw data into DuckDB

dbt seed



\# 3. Run transformation models

dbt run



\# 4. Run data quality tests

dbt test



\# 5. Query results

python query\_results.py

```



\---



\## Data Source

\- \*\*Baker Hughes Company Form 10-K\*\* — Fiscal Year ended December 31, 2023

\- Filed with SEC EDGAR on February 5, 2024

\- Source: https://www.sec.gov/Archives/edgar/data/0001701605/000170160524000033/bkr-20231231.htm



\---



\## Author

\*\*Muhammad Hassan\*\*  

GL Programmer → Analytics Engineering  

Houston, TX  

GitHub: \[@hassanm9301](https://github.com/hassanm9301)



