"""Download and extract CVM DFP annual files.

Source: https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/
Output: data/raw/ (zip files and the CSVs extracted from them)

Run from the project root:  python src/download_dfp.py
"""

import zipfile
from pathlib import Path

import requests

BASE_URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/"
YEARS = range(2021, 2026)  # 2021 to 2025 (the end of a range is not included)
RAW_DIR = Path("data") / "raw"


def download_zip(year):
    """Download the DFP zip file for one year and return its local path."""
    file_name = f"dfp_cia_aberta_{year}.zip"
    url = BASE_URL + file_name
    zip_path = RAW_DIR / file_name

    if zip_path.exists():
        print(f"{file_name} already exists, skipping download")
        return zip_path

    print(f"Downloading {url} ...")
    response = requests.get(url, timeout=60)
    response.raise_for_status() 

    with open(zip_path, "wb") as f:
        f.write(response.content)

    return zip_path


def extract_zip(zip_path):
    """Extract all CSV files from a zip into RAW_DIR."""
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(RAW_DIR)
    print(f"Extracted {zip_path.name}")


if __name__ == "__main__":
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for year in YEARS:
        zip_path = download_zip(year)
        extract_zip(zip_path)

    print("Done.")
