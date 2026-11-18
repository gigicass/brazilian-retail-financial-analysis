# Brazilian Retail Financial Analysis

Comparative financial analysis of four Brazilian listed retailers (Magazine Luiza,
Lojas Renner, Grupo SBF and C&A) from 2021 to 2025, built from CVM open data.

> Work in progress. Full description, how to run and dashboard link coming soon.

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
