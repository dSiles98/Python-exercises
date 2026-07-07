"""
Ejercicios 1.1 - 1.6 del curso de Python.
Autor: Dayana Siles

Patrones de diseño aplicados:
- Value Object: clase Stock encapsula datos de una acción (1.5).
- Separation of concerns: stats, pcost y Stock en responsabilidades distintas.
- Module pattern: portfolio_cost reutilizable con guardia __main__ (1.6).
"""

from __future__ import annotations

import io
import logging
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Rutas de datos del curso
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).resolve().parent.parent / "python-course" / "Data"

log = logging.getLogger(__name__)


# ===================================================================
# Ejercicio 1.1 — stats.py
# ===================================================================

GRADES: list[int] = [85, 92, 78, 90, 88]


def promedio(values: list[float]) -> float:
    """Calcula el promedio aritmético de una secuencia numérica."""
    if not values:
        raise ValueError("La lista de valores no puede estar vacía")
    return sum(values) / len(values)


def run_stats_demo() -> float:
    """Ejecuta la demostración de promedio de notas (ejercicio 1.1)."""
    average_grade = promedio(GRADES)
    print("Promedio:", average_grade)
    return average_grade


# ===================================================================
# Ejercicio 1.2 — Tipos integrados: números, cadenas, listas, diccionarios
# ===================================================================


def demonstrate_numeric_operations() -> dict[str, Any]:
    """Demuestra operaciones numéricas básicas del ejercicio 1.2."""
    sample_float = 1172.5
    sample_int = 12345
    return {
        "addition": 3 + 4 * 5,
        "true_division": 7 / 4,
        "floor_division": 7 // 4,
        "as_integer_ratio": sample_float.as_integer_ratio(),
        "is_integer": sample_float.is_integer(),
        "numerator": sample_int.numerator,
        "denominator": sample_int.denominator,
        "bit_length": sample_int.bit_length(),
    }


class SymbolSequence:
    """
    Encapsula manipulaciones de cadenas y listas de símbolos bursátiles.
    Patrón: Value Object / encapsulación de operaciones sobre secuencias.
    """

    def __init__(self, symbols_text: str = "AAPL IBM MSFT YHOO SCO") -> None:
        self._symbols_text = symbols_text

    @property
    def text(self) -> str:
        return self._symbols_text

    def slice_examples(self) -> dict[str, str]:
        return {
            "first_char": self._symbols_text[0],
            "last_char": self._symbols_text[-1],
            "first_symbol": self._symbols_text[:4],
            "last_symbol": self._symbols_text[-3:],
            "middle_symbol": self._symbols_text[5:8],
        }

    def append_symbol(self, symbol: str) -> str:
        self._symbols_text += f" {symbol}"
        return self._symbols_text

    def prepend_symbol(self, symbol: str) -> str:
        self._symbols_text = f"{symbol} {self._symbols_text}"
        return self._symbols_text

    def membership_checks(self) -> dict[str, bool]:
        return {
            "IBM": "IBM" in self._symbols_text,
            "AA": "AA" in self._symbols_text,
            "CAT": "CAT" in self._symbols_text,
        }

    def to_lowercase_copy(self) -> str:
        return self._symbols_text.lower()

    def remove_symbol(self, symbol: str) -> str:
        self._symbols_text = self._symbols_text.replace(symbol, "")
        return self._symbols_text

    def to_list(self) -> list[str]:
        return self._symbols_text.split()

    def mutate_list_operations(self) -> list[str]:
        """Replica el flujo completo de operaciones sobre listas del ejercicio 1.2."""
        symbol_list = self.to_list()
        symbol_list[2] = "AIG"
        symbol_list.append("RHT")
        symbol_list.insert(1, "AA")
        symbol_list.remove("MSFT")
        symbol_list.sort()
        symbol_list.sort(reverse=True)
        return symbol_list

    def nested_list_example(self) -> dict[str, Any]:
        symbol_list = self.mutate_list_operations()
        number_list = [101, 102, 103]
        nested_items = [symbol_list, number_list]
        return {
            "nested": nested_items,
            "inner_symbol": nested_items[0][1],
            "inner_char": nested_items[0][1][2],
            "number": nested_items[1][1],
        }


def demonstrate_dictionary_operations() -> dict[str, Any]:
    """Demuestra operaciones con diccionarios del ejercicio 1.2."""
    prices: dict[str, float] = {"IBM": 91.1, "GOOG": 490.1, "AAPL": 312.23}
    prices["IBM"] = 123.45
    prices["HPQ"] = 26.15
    keys_before_delete = list(prices)
    del prices["AAPL"]
    return {
        "ibm_price": 123.45,
        "keys_before_delete": keys_before_delete,
        "prices_after_delete": prices,
    }


# ===================================================================
# Ejercicios 1.3 - 1.6 — pcost.py
# ===================================================================


def portfolio_cost(
    portfolio_filename: str | Path,
    *,
    skip_invalid_lines: bool = False,
) -> float:
    """
    Calcula el costo total de un portafolio desde un archivo .dat.

    Cada línea tiene el formato: ``SYMBOL SHARES PRICE``.

    Args:
        portfolio_filename: Ruta al archivo del portafolio.
        skip_invalid_lines: Si es True, omite líneas inválidas con advertencia
            en lugar de propagar la excepción (ejercicio 1.4).
    """
    total_cost = 0.0
    portfolio_path = Path(portfolio_filename)

    with portfolio_path.open(encoding="utf-8") as portfolio_file:
        for line in portfolio_file:
            stripped_line = line.strip()
            if not stripped_line:
                continue

            fields = stripped_line.split()
            if len(fields) < 3:
                if skip_invalid_lines:
                    _log_parse_error(line, ValueError("not enough fields"))
                    continue
                raise ValueError(f"Línea inválida (campos insuficientes): {line!r}")

            stock_name, shares_text, price_text = fields[0], fields[1], fields[2]

            try:
                share_count = int(shares_text)
                unit_price = float(price_text)
            except ValueError as exc:
                if skip_invalid_lines:
                    _log_parse_error(line, exc)
                    continue
                raise

            total_cost += share_count * unit_price
            log.debug(
                "Procesado %s: %d acciones a %.2f", stock_name, share_count, unit_price
            )

    return total_cost


def _log_parse_error(raw_line: str, error: Exception) -> None:
    """Registra una línea que no pudo parsearse (ejercicio 1.4)."""
    print(f"Couldn't parse: {raw_line!r}")
    print(f"Reason: {error}")


def run_pcost_main(portfolio_filename: str | Path | None = None) -> float:
    """Punto de entrada cuando pcost se ejecuta como script principal (1.6)."""
    data_file = portfolio_filename or DATA_DIR / "portfolio.dat"
    total = portfolio_cost(data_file, skip_invalid_lines=True)
    print(total)
    return total


# ===================================================================
# Ejercicio 1.5 — stock.py
# ===================================================================


class Stock:
    """Representa una acción con nombre, cantidad y precio unitario."""

    def __init__(self, name: str, shares: int, price: float) -> None:
        self.name = name
        self.shares = shares
        self.price = price

    def cost(self) -> float:
        return self.shares * self.price

    def __repr__(self) -> str:
        return f"Stock({self.name!r}, {self.shares}, {self.price})"


def format_stock_line(stock_position: Stock) -> str:
    """Formatea una posición para impresión tabular."""
    return f"{stock_position.name:>10s} {stock_position.shares:10d} {stock_position.price:10.2f}"


# ===================================================================
# Pruebas unitarias
# ===================================================================


class TestStats(unittest.TestCase):
    def test_promedio_grades(self) -> None:
        self.assertAlmostEqual(promedio(GRADES), 86.6)

    def test_promedio_empty_raises(self) -> None:
        with self.assertRaises(ValueError):
            promedio([])

    def test_stats_demo_output(self) -> None:
        output_buffer = io.StringIO()
        with redirect_stdout(output_buffer):
            result = run_stats_demo()
        self.assertAlmostEqual(result, 86.6)
        self.assertIn("Promedio: 86.6", output_buffer.getvalue())


class TestBuiltinTypes(unittest.TestCase):
    def test_numeric_operations(self) -> None:
        results = demonstrate_numeric_operations()
        self.assertEqual(results["addition"], 23)
        self.assertEqual(results["true_division"], 1.75)
        self.assertEqual(results["floor_division"], 1)
        self.assertEqual(results["as_integer_ratio"], (2345, 2))
        self.assertFalse(results["is_integer"])

    def test_string_is_immutable(self) -> None:
        symbol_sequence = SymbolSequence()
        with self.assertRaises(TypeError):
            symbol_sequence.text[0] = "a"  # type: ignore[index]

    def test_string_slice_and_membership(self) -> None:
        symbol_sequence = SymbolSequence()
        slices = symbol_sequence.slice_examples()
        self.assertEqual(slices["first_symbol"], "AAPL")
        self.assertEqual(slices["middle_symbol"], "IBM")

        symbol_sequence.append_symbol("GOOG")
        symbol_sequence.prepend_symbol("HPQ")
        membership = symbol_sequence.membership_checks()
        self.assertTrue(membership["IBM"])
        self.assertTrue(membership["AA"])
        self.assertFalse(membership["CAT"])

    def test_list_mutations(self) -> None:
        symbol_sequence = SymbolSequence("HPQ AAPL IBM MSFT YHOO  GOOG")
        symbol_list = symbol_sequence.mutate_list_operations()
        self.assertEqual(symbol_list[0], "YHOO")
        self.assertNotIn("MSFT", symbol_list)
        self.assertIn("AA", symbol_list)

    def test_nested_lists(self) -> None:
        symbol_sequence = SymbolSequence("HPQ AAPL IBM MSFT YHOO  GOOG")
        nested = symbol_sequence.nested_list_example()
        self.assertEqual(nested["inner_char"], "T")
        self.assertEqual(nested["number"], 102)

    def test_dictionary_operations(self) -> None:
        results = demonstrate_dictionary_operations()
        self.assertEqual(results["ibm_price"], 123.45)
        self.assertNotIn("AAPL", results["prices_after_delete"])


class TestPortfolioCost(unittest.TestCase):
    def test_portfolio_dat_cost(self) -> None:
        portfolio_path = DATA_DIR / "portfolio.dat"
        if not portfolio_path.exists():
            self.skipTest("portfolio.dat no disponible")
        self.assertAlmostEqual(portfolio_cost(portfolio_path), 44671.15)

    def test_portfolio2_dat_cost(self) -> None:
        portfolio_path = DATA_DIR / "portfolio2.dat"
        if not portfolio_path.exists():
            self.skipTest("portfolio2.dat no disponible")
        self.assertAlmostEqual(portfolio_cost(portfolio_path), 19908.75)

    def test_portfolio3_skips_invalid_lines(self) -> None:
        portfolio_path = DATA_DIR / "portfolio3.dat"
        if not portfolio_path.exists():
            self.skipTest("portfolio3.dat no disponible")

        output_buffer = io.StringIO()
        with redirect_stdout(output_buffer):
            total_cost = portfolio_cost(portfolio_path, skip_invalid_lines=True)

        self.assertAlmostEqual(total_cost, 12597.48)
        error_output = output_buffer.getvalue()
        self.assertIn("Couldn't parse:", error_output)
        self.assertIn("invalid literal for int()", error_output)

    def test_invalid_line_without_skip_raises(self) -> None:
        portfolio_path = DATA_DIR / "portfolio3.dat"
        if not portfolio_path.exists():
            self.skipTest("portfolio3.dat no disponible")
        with self.assertRaises(ValueError):
            portfolio_cost(portfolio_path, skip_invalid_lines=False)

    def test_main_guard_prints_total(self) -> None:
        portfolio_path = DATA_DIR / "portfolio.dat"
        if not portfolio_path.exists():
            self.skipTest("portfolio.dat no disponible")

        output_buffer = io.StringIO()
        with redirect_stdout(output_buffer):
            total = run_pcost_main(portfolio_path)

        self.assertAlmostEqual(total, 44671.15)
        self.assertIn("44671.15", output_buffer.getvalue())


class TestStock(unittest.TestCase):
    def test_stock_attributes_and_cost(self) -> None:
        google_position = Stock("GOOG", 100, 490.10)
        self.assertEqual(google_position.name, "GOOG")
        self.assertEqual(google_position.shares, 100)
        self.assertAlmostEqual(google_position.price, 490.1)
        self.assertAlmostEqual(google_position.cost(), 49010.0)

    def test_stock_format_line(self) -> None:
        google_position = Stock("GOOG", 100, 490.10)
        formatted = format_stock_line(google_position)
        self.assertEqual(formatted, "      GOOG        100     490.10")

    def test_multiple_stock_instances(self) -> None:
        ibm_position = Stock("IBM", 50, 91.5)
        self.assertAlmostEqual(ibm_position.cost(), 4575.0)


class TestModuleImport(unittest.TestCase):
    def test_portfolio_cost_importable_without_side_effects(self) -> None:
        """Simula import de pcost sin ejecutar el bloque __main__ (ejercicio 1.6)."""
        portfolio_path = DATA_DIR / "portfolio2.dat"
        if not portfolio_path.exists():
            self.skipTest("portfolio2.dat no disponible")

        output_buffer = io.StringIO()
        with redirect_stdout(output_buffer):
            cost = portfolio_cost(portfolio_path)

        self.assertAlmostEqual(cost, 19908.75)
        self.assertEqual(output_buffer.getvalue(), "")


def _demo_exercises() -> None:
    """Verificaciones rápidas de los ejercicios 1.1-1.6."""
    assert promedio(GRADES) == 86.6
    assert demonstrate_numeric_operations()["addition"] == 23

    symbol_sequence = SymbolSequence()
    assert symbol_sequence.slice_examples()["first_char"] == "A"

    google_position = Stock("GOOG", 100, 490.10)
    assert google_position.cost() == 49010.0

    portfolio_path = DATA_DIR / "portfolio.dat"
    if portfolio_path.exists():
        assert abs(portfolio_cost(portfolio_path) - 44671.15) < 0.01

    print("Todas las demostraciones del capítulo 1 pasaron correctamente.")


if __name__ == "__main__":
    unittest.main()
