"""
Pipeline generador para ticker bursátil (ejercicio 8.2).
"""

from __future__ import annotations

import csv
from pathlib import Path

from follow import follow
from structly import Float, Integer, String, Structure, create_formatter, print_table


class Ticker(Structure):
    name = String()
    price = Float()
    date = String()
    time = String()
    change = Float()
    open = Float()
    high = Float()
    low = Float()
    volume = Integer()


def build_negative_change_pipeline(log_file_path: str | Path):
    """Monta un pipeline de generadores para registros con cambio negativo."""
    csv_lines = follow(log_file_path)
    csv_rows = csv.reader(csv_lines)
    ticker_records = (Ticker.from_row(row) for row in csv_rows)
    negative_records = (record for record in ticker_records if record.change < 0)
    return negative_records


if __name__ == "__main__":
    data_dir = Path(__file__).resolve().parent.parent / "python-course" / "Data"
    log_path = data_dir / "stocklog.csv"
    formatter = create_formatter("text")
    negative_tickers = build_negative_change_pipeline(log_path)
    print_table(negative_tickers, ["name", "price", "change"], formatter)
