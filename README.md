# Brazilian Retail Financial Analysis

Comparative financial analysis of four Brazilian listed retailers (Magazine Luiza,
Lojas Renner, Grupo SBF and C&A) from 2021 to 2025, built from CVM open data.

**[Open the interactive dashboard](https://brazilian-retail-analysis.streamlit.app/)**

## The problem

Brazilian listed companies publish their financial statements in a standard format
(DFP) on the CVM open data portal, but the files are large, cover every listed company
and mix several statements, versions and scales. Comparing a handful of companies
over time takes a lot of manual work.

This project builds a reproducible pipeline that downloads the raw files, keeps only
what is needed, checks it, and turns it into six financial ratios shown in a dashboard
where the user picks the companies and the ratio.

## Key insights

- **Lojas Renner** has the strongest profile of the group: the highest gross margin
  (58.4% in 2021 to 61.7% in 2025) and the lowest debt ratio, which fell from 54.2% to 46.7%.
- **Magazine Luiza** sells mostly third-party brands, so its gross margin (24-31%) is about
  half of the fashion retailers'. It reported net losses in 2022 and 2023: in 2022 its
  operating income was still positive, so the loss came from the financial result and taxes,
  in a period of high interest rates in Brazil.
- **C&A** is the turnaround story: its operating margin went from 1.8% in 2021 to 13.1% in 2025,
  the highest of the group. Its 2021 net income, however, came almost entirely from a one-off
  tax gain (see the notes in the Validation section).
- **Debt ratios of 60-75%** are common in retail: since IFRS 16, store leases are recognized
  as liabilities. Lojas Renner is the exception.

## Data source

[CVM open data portal](https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/),
dataset *Companhias Abertas: Documentos: DFP* (annual standardized financial statements).
One zip file per year, with CSV files separated by `;` and encoded in `latin-1`.

| Company | CVM code |
|---|---|
| Magazine Luiza | 22470 |
| Lojas Renner | 8133 |
| Grupo SBF | 24694 |
| C&A | 24848 |

## Methodology

**Cleaning** (`src/build_financials.py`)

- Only **consolidated** statements (`_con` files): balance sheet (BPA, BPP) and income statement (DRE).
- Only the **current fiscal year** of each file (`ORDEM_EXERC = "ÚLTIMO"`), so each year appears once.
- All values converted to reais using `ESCALA_MOEDA` (thousands or units).
- Only **fixed CVM accounts** (`ST_CONTA_FIXA = "S"`), which mean the same thing for every company:

| Code | Account |
|---|---|
| 1 | Total assets |
| 1.01 | Current assets |
| 2.01 | Current liabilities |
| 2.02 | Non-current liabilities |
| 2.03 | Equity |
| 3.01 | Net revenue |
| 3.03 | Gross profit |
| 3.05 | Operating income (before financial result and taxes) |
| 3.11 | Net income |

Automatic checks stop the pipeline if a scale is unknown, an account is missing or duplicated,
a company-year is missing, or the balance sheet does not balance (assets = liabilities + equity).

**Ratios** (`src/compute_ratios.py`)

| Ratio | Formula |
|---|---|
| Current ratio | Current assets / current liabilities |
| Gross margin | Gross profit / net revenue |
| Operating margin | Operating income / net revenue |
| Net margin | Net income / net revenue |
| ROE | Net income / equity (end of year) |
| Debt ratio | (Current + non-current liabilities) / total assets |

## Project structure

```
├── app.py                        # Streamlit dashboard
├── data/processed/ratios.csv     # final table used by the dashboard
├── notebooks/
│   ├── 01_data_cleaning.ipynb    # step-by-step exploration of the cleaning
│   └── 02_visualization.ipynb    # charts and first insights
├── src/
│   ├── download_dfp.py           # downloads and extracts the CVM files
│   ├── build_financials.py       # filters, converts and maps the accounts
│   └── compute_ratios.py         # computes the six ratios
└── requirements.txt
```

Raw data is not versioned: it can be rebuilt with the scripts. Only the small final
table (`ratios.csv`) is committed, so the dashboard can run online.

## How to run

```bash
git clone https://github.com/gigicass/brazilian-retail-financial-analysis.git
cd brazilian-retail-financial-analysis

python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

python src/download_dfp.py       # data/raw/
python src/build_financials.py   # data/processed/financials.csv
python src/compute_ratios.py     # data/processed/ratios.csv

streamlit run app.py
```

Run the scripts from the project root. The dashboard alone (`streamlit run app.py`)
works right after cloning, since `ratios.csv` is in the repository.

## Validation

To make sure the pipeline (filters, scale and account mapping) produces correct
numbers, a sample of values was compared with two external references:

1. **The DFP document filed by each company with CVM** (audited financial statements,
   consolidated, current fiscal year).
2. **The earnings release** published on the company's investor relations (IR) website.

### 1. DFP filed with CVM

Values in **R$ thousands**. All 17 values match exactly.

| Company | Year | Account | This project | DFP filed with CVM | Match |
|---|---|---|---:|---:|:---:|
| Magazine Luiza | 2025 | `net_revenue` | 38,703,387 | 38,703,387 | ✅ |
| Magazine Luiza | 2025 | `net_income` | 204,603 | 204,603 | ✅ |
| Magazine Luiza | 2025 | `total_assets` | 37,911,158 | 37,911,158 | ✅ |
| Magazine Luiza | 2025 | `equity` | 11,278,030 | 11,278,030 | ✅ |
| Lojas Renner | 2025 | `net_revenue` | 15,829,460 | 15,829,460 | ✅ |
| Lojas Renner | 2025 | `net_income` | 1,457,566 | 1,457,566 | ✅ |
| Lojas Renner | 2025 | `total_assets` | 19,626,027 | 19,626,027 | ✅ |
| Lojas Renner | 2025 | `equity` | 10,456,281 | 10,456,281 | ✅ |
| Grupo SBF | 2025 | `net_revenue` | 7,736,413 | 7,736,413 | ✅ |
| Grupo SBF | 2025 | `net_income` | 327,970 | 327,970 | ✅ |
| Grupo SBF | 2025 | `total_assets` | 9,522,546 | 9,522,546 | ✅ |
| Grupo SBF | 2025 | `equity` | 3,059,794 | 3,059,794 | ✅ |
| C&A | 2025 | `net_revenue` | 7,982,958 | 7,982,958 | ✅ |
| C&A | 2025 | `net_income` | 587,087 | 587,087 | ✅ |
| C&A | 2025 | `total_assets` | 9,318,633 | 9,318,633 | ✅ |
| C&A | 2025 | `equity` | 3,707,056 | 3,707,056 | ✅ |
| C&A | 2021 | `net_income` | 329,009 | 329,009 | ✅ |

Sources (CVM document system):
[Magazine Luiza 2025](https://www.rad.cvm.gov.br/ENETCONSULTA/frmDownloadDocumento.aspx?CodigoInstituicao=1&NumeroSequencialDocumento=155314) ·
[Lojas Renner 2025](https://www.rad.cvm.gov.br/ENETCONSULTA/frmDownloadDocumento.aspx?CodigoInstituicao=1&NumeroSequencialDocumento=155117) ·
[Grupo SBF 2025](https://www.rad.cvm.gov.br/ENETCONSULTA/frmDownloadDocumento.aspx?CodigoInstituicao=1&NumeroSequencialDocumento=155192) ·
[C&A 2025](https://www.rad.cvm.gov.br/ENETCONSULTA/frmDownloadDocumento.aspx?CodigoInstituicao=1&NumeroSequencialDocumento=154859) ·
[C&A 2021](https://www.rad.cvm.gov.br/ENETCONSULTA/frmDownloadDocumento.aspx?CodigoInstituicao=1&NumeroSequencialDocumento=112425)

### 2. Earnings releases (IR websites)

Values in **R$ millions**, as shown in the releases.

| Company | Year | Account | This project | Release | Match |
|---|---|---|---:|---:|:---:|
| Magazine Luiza | 2025 | `net_revenue` | 38,703.4 | 38,703.4 | ✅ |
| Magazine Luiza | 2025 | `net_income` | 204.6 | 204.6 | ✅ |
| Magazine Luiza | 2025 | `total_assets` | 37,911.2 | 37,911.2 | ✅ |
| Magazine Luiza | 2025 | `equity` | 11,278.0 | 11,278.0 | ✅ |
| Lojas Renner | 2025 | `net_revenue` | 15,829.5 | 15,829.5 | ✅ |
| Lojas Renner | 2025 | `net_income` | 1,457.6 | 1,457.6 | ✅ |
| Lojas Renner | 2025 | `total_assets` | 19,626.0 | 19,625.9 | ⚠️ |
| Lojas Renner | 2025 | `equity` | 10,456.3 | 10,456.1 | ⚠️ |

Sources:
[Magazine Luiza 4Q25 release](https://ri.magazineluiza.com.br/Download/Release-de-Resultado?=OHnwGLiAvm2nPO11N4SHvw==&linguagem=pt) ·
[Lojas Renner 4Q25 release](https://api.mziq.com/mzfilemanager/v2/d/13154776-9416-4fce-8c46-3e54d45b03a3/f114f0ab-65d4-6ea1-5439-aaaa83896104?origin=2)

⚠️ The Lojas Renner release shows total assets and equity about R$ 0.1-0.2 million
below the DFP. Both DFP versions filed with CVM (1 and 2) contain the same values as
this project, so the difference comes from the release, an unaudited document,
not from the pipeline. The audited DFP is used as the reference.

### Notes

- `net_income` and `equity` include non-controlling interests (CVM accounts 3.11 and 2.03).
- Lojas Renner filed two versions of its 2025 DFP; the open data files keep only the latest one.
- C&A's 2021 net income (R$ 329 million) was higher than its operating income (R$ 93 million)
  because of a positive income tax line. In September 2021 the Supreme Court (STF) ruled
  that IRPJ/CSLL are not due on the Selic interest received on tax refunds, and C&A recognized
  a R$ 311 million deferred tax asset (DFP 2021, note 14). According to the management report,
  without these unrealized tax gains C&A would have reported a net loss in 2021.

## Limitations

- Four companies only; Magazine Luiza has a different business model (electronics and
  third-party brands), so its margins are best compared over time, not against the fashion retailers.
- ROE uses end-of-year equity, not average equity.
- One-off items are not removed from the ratios. They are flagged in the dashboard when
  confirmed in the notes to the financial statements (so far, C&A 2021). Grupo SBF also had
  a positive income tax line in 2021, not yet checked against its notes.

## Tools

Python, pandas, matplotlib, Altair, Streamlit, Git.

## Author

Giovanna Cavalcanti, Accounting student at FEA/USP and BI analyst.
