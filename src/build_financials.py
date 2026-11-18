"""Build a clean table of key accounts from the raw CVM DFP files.

Input:  data/raw/      (created by src/download_dfp.py)
Output: data/processed/financials.csv  (one row per company and year)

Run from the project root:  python src/build_financials.py
The step-by-step exploration behind this script is in notebooks/01_data_cleaning.ipynb.
"""

from pathlib import Path

import pandas as pd

RAW_DIR = Path("data") / "raw"
PROCESSED_DIR = Path("data") / "processed"

YEARS = range(2021, 2026)
STATEMENTS = ["BPA", "BPP", "DRE"]

COMPANIES = {
    22470: "Magazine Luiza",
    8133: "Lojas Renner",
    24694: "Grupo SBF",
    24848: "C&A",
}

SCALE_FACTOR = {"UNIDADE": 1, "MIL": 1000}

# Fixed CVM account codes -> our column names
ACCOUNTS = {
    "1": "total_assets",
    "1.01": "current_assets",
    "2.01": "current_liabilities",
    "2.02": "noncurrent_liabilities",
    "2.03": "equity",
    "3.01": "net_revenue",
    "3.03": "gross_profit",
    "3.05": "operating_income",
    "3.11": "net_income",
}


def load_statement(statement, year):
    """Read one consolidated statement file and keep our companies, current year only."""
    path = RAW_DIR / f"dfp_cia_aberta_{statement}_con_{year}.csv"
    df = pd.read_csv(path, sep=";", encoding="latin-1")

    is_our_company = df["CD_CVM"].isin(COMPANIES.keys())
    is_current_year = df["ORDEM_EXERC"] == "ÚLTIMO"
    df = df[is_our_company & is_current_year].copy()

    df["STATEMENT"] = statement
    df["YEAR"] = year
    return df


def load_all_statements():
    """Load every statement for every year into a single table."""
    frames = []
    for statement in STATEMENTS:
        for year in YEARS:
            frames.append(load_statement(statement, year))
    return pd.concat(frames, ignore_index=True)


def convert_to_reais(statements):
    """Add a VALUE column with every amount in reais."""
    statements["SCALE_FACTOR"] = statements["ESCALA_MOEDA"].map(SCALE_FACTOR)

    if statements["SCALE_FACTOR"].isna().any():
        unknown = statements[statements["SCALE_FACTOR"].isna()]["ESCALA_MOEDA"].unique()
        raise ValueError(f"Unknown scale(s) in ESCALA_MOEDA: {unknown}")

    statements["VALUE"] = statements["VL_CONTA"] * statements["SCALE_FACTOR"]
    return statements


def select_accounts(statements):
    """Keep only the mapped fixed accounts and check that none is missing."""
    selected = statements[statements["CD_CONTA"].isin(ACCOUNTS.keys())].copy()
    selected["ACCOUNT"] = selected["CD_CONTA"].map(ACCOUNTS)

    if not (selected["ST_CONTA_FIXA"] == "S").all():
        raise ValueError("Some selected accounts are not fixed CVM accounts")

    accounts_per_company_year = selected.groupby(["CD_CVM", "YEAR"]).size()
    if not (accounts_per_company_year == len(ACCOUNTS)).all():
        raise ValueError("Some company/year is missing accounts or has duplicates")

    expected_rows = len(COMPANIES) * len(YEARS)
    if len(accounts_per_company_year) != expected_rows:
        raise ValueError(f"Expected {expected_rows} company-years, found {len(accounts_per_company_year)}")

    return selected


def to_wide_table(selected):
    """Reshape to one row per company and year, one column per account."""
    financials = selected.pivot(index=["CD_CVM", "YEAR"], columns="ACCOUNT", values="VALUE")
    financials = financials.reset_index()
    financials["COMPANY"] = financials["CD_CVM"].map(COMPANIES)

    columns_order = ["COMPANY", "CD_CVM", "YEAR"] + list(ACCOUNTS.values())
    financials = financials[columns_order]
    financials.columns.name = None
    return financials


def check_balance_sheet(financials):
    """Assets must equal liabilities plus equity in every row."""
    liabilities_and_equity = (
        financials["current_liabilities"]
        + financials["noncurrent_liabilities"]
        + financials["equity"]
    )
    difference = (financials["total_assets"] - liabilities_and_equity).abs()

    if (difference > 1).any():  # tolerance of R$ 1 for rounding
        raise ValueError("Balance sheet does not balance for some company/year")


if __name__ == "__main__":
    statements = load_all_statements()
    statements = convert_to_reais(statements)
    selected = select_accounts(statements)
    financials = to_wide_table(selected)
    check_balance_sheet(financials)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PROCESSED_DIR / "financials.csv"
    financials.to_csv(output_path, index=False)

    print(f"Saved {len(financials)} rows to {output_path}")
