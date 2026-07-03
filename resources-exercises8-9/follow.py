"""
Generador que sigue nuevas líneas al final de un archivo (ejercicios 8.1 y 8.4).
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Generator, Iterator


def follow(log_file_path: str | Path) -> Generator[str, None, None]:
    """
    Genera líneas nuevas escritas al final de un archivo de log.
    Patrón: Generator / Iterator.
    """
    try:
        with open(log_file_path, "r") as log_file:
            log_file.seek(0, os.SEEK_END)
            while True:
                line = log_file.readline()
                if line == "":
                    time.sleep(0.1)
                    continue
                yield line
    except GeneratorExit:
        print("Following Done")


def frange(
    start: float, stop: float, step: float
) -> Generator[float, None, None]:
    """Genera un rango con pasos fraccionarios (ejercicio 8.1a)."""
    current_value = start
    while current_value < stop:
        yield current_value
        current_value += step


class FractionalRange:
    """Rango fraccionario reutilizable (ejercicio 8.1a)."""

    def __init__(self, start: float, stop: float, step: float) -> None:
        self.start = start
        self.stop = stop
        self.step = step

    def __iter__(self) -> Iterator[float]:
        current_value = self.start
        while current_value < self.stop:
            yield current_value
            current_value += self.step


if __name__ == "__main__":
    data_dir = Path(__file__).resolve().parent.parent / "python-course" / "Data"
    log_path = data_dir / "stocklog.csv"

    for log_line in follow(log_path):
        fields = log_line.split(",")
        stock_name = fields[0].strip('"')
        stock_price = float(fields[1])
        price_change = float(fields[4])
        if price_change < 0:
            print(f"{stock_name:>10s} {stock_price:10.2f} {price_change:10.2f}")
