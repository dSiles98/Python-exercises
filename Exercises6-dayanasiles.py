"""
Ejercicios 6.1 - 6.5 del curso de Python.
Autor: Dayana Siles

Punto de entrada que importa los módulos del curso y ejecuta todas las pruebas.

Módulos:
    structure.py   — Clase base Structure (ejercicios 6.1-6.4)
    stock.py       — Clase Stock sobre Structure
    orig_stock.py  — Respaldo de la implementación pre-6.1
    validate.py    — Validadores y ValidatedFunction (ejercicio 6.5)
    teststock.py   — Pruebas de Stock
    teststructure.py — Pruebas de Structure
    testvalidate.py  — Pruebas de ValidatedFunction
"""

from __future__ import annotations

import csv
import inspect
import unittest
from pathlib import Path

import stock
from structure import Date
from validate import Integer, validated

DATA_DIR = Path(__file__).resolve().parent.parent / "python-course" / "Data"


def _demo_exercises() -> None:
    """Verificaciones interactivas de los ejercicios 6.1-6.5."""

    stock_position = stock.Stock("GOOG", 100, 490.1)
    assert stock_position.name == "GOOG"
    assert repr(stock_position) == "Stock('GOOG', 100, 490.1)"

    keyword_position = stock.Stock(name="GOOG", price=490.1, shares=50)
    assert keyword_position.shares == 50

    current_date = Date(2026, 7, 3)
    assert repr(current_date) == "Date(2026, 7, 3)"

    init_signature = inspect.signature(stock.Stock.__init__)
    parameter_names = tuple(init_signature.parameters)
    assert parameter_names == ("self", "name", "shares", "price")

    @validated
    def multiply(first: Integer, second: Integer) -> Integer:
        return first * second

    assert multiply(3, 4) == 12

    portfolio_path = DATA_DIR / "portfolio.csv"
    if portfolio_path.exists():
        with open(portfolio_path) as portfolio_file:
            csv_reader = csv.reader(portfolio_file)
            next(csv_reader)
            first_row = next(csv_reader)
        parsed_stock = stock.Stock.from_row(first_row)
        assert parsed_stock.name == "AA"

    print("Todas las demostraciones del capítulo 6 pasaron correctamente.")


def _run_all_tests(verbosity: int = 2) -> unittest.TestResult:
    """Ejecuta teststock, teststructure y testvalidate."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromName("teststock"))
    suite.addTests(loader.loadTestsFromName("teststructure"))
    suite.addTests(loader.loadTestsFromName("testvalidate"))
    return unittest.TextTestRunner(verbosity=verbosity).run(suite)


if __name__ == "__main__":
    _run_all_tests()
