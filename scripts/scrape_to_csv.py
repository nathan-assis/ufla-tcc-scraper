# python -m scripts.scrape_to_csv

import csv
from pathlib import Path

from src.utils.scraper import scrape


OUTPUT_PATH = Path(__file__).resolve().parents[1] / "assets" / "output" / "data.csv"
FIELDNAMES = ["id", "curso", "titulo", "autor", "orientador", "resumo", "url"]


def main() -> None:
    tccs_data = scrape()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES)
        writer.writeheader()
        for tcc_id, tcc in tccs_data.items():
            writer.writerow({"id": tcc_id, **tcc})

    print(f"CSV salvo: {OUTPUT_PATH} ({len(tccs_data)} registros)")


if __name__ == "__main__":
    main()
