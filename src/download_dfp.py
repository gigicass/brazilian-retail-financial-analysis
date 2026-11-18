import zipfile
from pathlib import Path

import requests

BASE_URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/"
YEARS = range(2021, 2026) 
RAW_DIR = Path("data") / "raw"


def download_zip(year):
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
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(RAW_DIR)
    print(f"Extracted {zip_path.name}")


if __name__ == "__main__":
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for year in YEARS:
        zip_path = download_zip(year)
        extract_zip(zip_path)

    print("Done.")
