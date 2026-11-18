"""Compute financial ratios for each company and year.

Input:  data/processed/financials.csv  (created by src/build_financials.py)
Output: data/processed/ratios.csv

Run from the project root:  python src/compute_ratios.py
"""

from pathlib import Path

import pandas as pd

PROCESSED_DIR = Path("data") / "processed"

# Accounts used as denominators: a zero would make a ratio meaningless
DENOMINATORS = ["current_liabilities", "net_revenue", "equity", "total_assets"]


def compute_ratios(financials):
    """Return a table with one row per company and year and one column per ratio."""
    ratios = financials[["COMPANY", "CD_CVM", "YEAR"]].copy()

    total_liabilities = financials["current_liabilities"] + financials["noncurrent_liabilities"]

    # Liquidity
    ratios["current_ratio"] = financials["current_assets"] / financials["current_liabilities"]

    # Profitability (as a share of net revenue)
    ratios["gross_margin"] = financials["gross_profit"] / financials["net_revenue"]
    ratios["operating_margin"] = financials["operating_income"] / financials["net_revenue"]
    ratios["net_margin"] = financials["net_income"] / financials["net_revenue"]

    # Return to shareholders (equity at the end of the year)
    ratios["roe"] = financials["net_income"] / financials["equity"]

    # Leverage: share of assets financed by third parties
    ratios["debt_ratio"] = total_liabilities / financials["total_assets"]

    return ratios


if __name__ == "__main__":
    financials = pd.read_csv(PROCESSED_DIR / "financials.csv")

    for column in DENOMINATORS:
        if (financials[column] <= 0).any():
            raise ValueError(f"Zero or negative values in {column}: ratios would be misleading")

    ratios = compute_ratios(financials)

    output_path = PROCESSED_DIR / "ratios.csv"
    ratios.to_csv(output_path, index=False)

    print(f"Saved {len(ratios)} rows to {output_path}")
