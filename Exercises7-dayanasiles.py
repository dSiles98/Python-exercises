"""
Ejercicios 7.1 - 7.6 del curso de Python.
Autor: Dayana Siles

Punto de entrada que ejecuta pruebas y demostraciones del capítulo 7.

Módulos:
    logcall.py    — Decoradores logged y logformat (7.1, 7.2)
    validate.py   — Decoradores validated y enforce (7.1, 7.2)
    structure.py  — Structure, metaclase, typed_structure (7.3-7.6)
    stock.py      — Stock sin imports de validators (7.6)
    mymeta.py     — Metaclase de demostración (7.5)
    reader.py     — Lectura CSV (7.6)
"""

from __future__ import annotations

import io
import importlib
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import reader
import stock
from logcall import logformat, logged
from structure import Date, Structure, typed_structure
from validate import Integer, PositiveFloat, PositiveInteger, String, enforce, validated

DATA_DIR = Path(__file__).resolve().parent.parent / "python-course" / "Data"


# ---------------------------------------------------------------------------
# Ejercicio 7.1 — sample.py
# ---------------------------------------------------------------------------


@logged
def add(x: int, y: int) -> int:
    return x + y


@logged
def subtract(x: int, y: int) -> int:
    return x - y


# ---------------------------------------------------------------------------
# Ejercicio 7.2 — decoradores con argumentos y métodos
# ---------------------------------------------------------------------------


@logformat("{func.__code__.co_filename}:{func.__name__}")
def multiply(x: int, y: int) -> int:
    return x * y


class Spam:
    """Demuestra el orden correcto de decoradores con métodos (ej. 7.2c)."""

    @logformat("{func.__name__}")
    def instance_method(self) -> None:
        pass

    @classmethod
    @logformat("{func.__name__}")
    def class_method(cls) -> None:
        pass

    @staticmethod
    @logformat("{func.__name__}")
    def static_method() -> None:
        pass

    @property
    @logformat("{func.__name__}")
    def property_method(self) -> None:
        pass


# ---------------------------------------------------------------------------
# Ejercicio 7.1/7.2 — funciones validadas
# ---------------------------------------------------------------------------


@validated
def validated_add(first: Integer, second: Integer) -> Integer:
    return first + second


@validated
def validated_pow(base: Integer, exponent: Integer) -> Integer:
    return base**exponent


@enforce(x=Integer, y=Integer, return_=Integer)
def enforced_add(x: int, y: int) -> int:
    return x + y


# ---------------------------------------------------------------------------
# Pruebas del capítulo 7
# ---------------------------------------------------------------------------


class TestLogcall(unittest.TestCase):
    def test_logged_preserves_metadata(self) -> None:
        @logged
        def sample_function() -> str:
            """Documentación de prueba."""
            return "ok"

        self.assertEqual(sample_function.__name__, "sample_function")
        self.assertEqual(sample_function.__doc__, "Documentación de prueba.")

    def test_spam_methods_with_correct_decorator_order(self) -> None:
        spam_instance = Spam()
        output_buffer = io.StringIO()

        with redirect_stdout(output_buffer):
            spam_instance.instance_method()
            Spam.class_method()
            Spam.static_method()
            _ = spam_instance.property_method

        logged_output = output_buffer.getvalue().strip().splitlines()
        self.assertEqual(
            logged_output,
            ["instance_method", "class_method", "static_method", "property_method"],
        )


class TestChapter7Validation(unittest.TestCase):
    def test_validated_add_success(self) -> None:
        self.assertEqual(validated_add(2, 3), 5)

    def test_validated_add_rejects_strings(self) -> None:
        with self.assertRaises(TypeError) as error_context:
            validated_add("2", "3")

        error_message = str(error_context.exception)
        self.assertIn("Bad Arguments", error_message)
        self.assertIn("Expected", error_message)

    def test_validated_pow_rejects_negative_exponent(self) -> None:
        with self.assertRaises(TypeError) as error_context:
            validated_pow(2, -1)

        self.assertIn("Bad return", str(error_context.exception))

    def test_enforce_matches_validated_behavior(self) -> None:
        self.assertEqual(enforced_add(2, 3), 5)
        with self.assertRaises(TypeError):
            enforced_add("2", "3")


class TestTypedStructure(unittest.TestCase):
    def test_typed_structure_factory(self) -> None:
        DynamicStock = typed_structure(
            "DynamicStock",
            name=String(),
            shares=PositiveInteger(),
            price=PositiveFloat(),
        )
        dynamic_position = DynamicStock("GOOG", 100, 490.1)
        self.assertEqual(dynamic_position.name, "GOOG")
        self.assertEqual(repr(dynamic_position), "DynamicStock('GOOG', 100, 490.1)")


class TestMetaclass(unittest.TestCase):
    def test_validator_registry_contains_expected_types(self) -> None:
        from validate import Validator

        expected_validator_names = {
            "Typed",
            "Integer",
            "Float",
            "String",
            "Positive",
            "PositiveInteger",
            "PositiveFloat",
        }
        self.assertTrue(expected_validator_names.issubset(Validator.validators.keys()))

    def test_stock_without_explicit_validator_imports(self) -> None:
        """Verifica que stock.py no necesita importar validators (ej. 7.6)."""
        stock_position = stock.Stock("GOOG", 100, 490.1)
        self.assertEqual(stock_position.name, "GOOG")

    def test_date_structure_still_works(self) -> None:
        current_date = Date(2026, 7, 3)
        self.assertEqual(repr(current_date), "Date(2026, 7, 3)")


class TestReaderIntegration(unittest.TestCase):
    def test_read_portfolio_csv(self) -> None:
        portfolio_path = DATA_DIR / "portfolio.csv"
        if not portfolio_path.exists():
            self.skipTest("Archivo portfolio.csv no disponible")

        portfolio = reader.read_csv_as_instances(portfolio_path, stock.Stock)
        self.assertEqual(len(portfolio), 7)
        self.assertEqual(portfolio[0].name, "AA")
        self.assertIsInstance(portfolio[0], stock.Stock)


def _run_all_tests(verbosity: int = 2) -> unittest.TestResult:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromModule(importlib.import_module("teststock")))
    suite.addTests(loader.loadTestsFromModule(importlib.import_module("teststructure")))
    suite.addTests(loader.loadTestsFromModule(importlib.import_module("testvalidate")))
    suite.addTests(loader.loadTestsFromTestCase(TestLogcall))
    suite.addTests(loader.loadTestsFromTestCase(TestChapter7Validation))
    suite.addTests(loader.loadTestsFromTestCase(TestTypedStructure))
    suite.addTests(loader.loadTestsFromTestCase(TestMetaclass))
    suite.addTests(loader.loadTestsFromTestCase(TestReaderIntegration))
    return unittest.TextTestRunner(verbosity=verbosity).run(suite)


def _demo_exercises() -> None:
    """Demostraciones interactivas del capítulo 7."""
    stock_position = stock.Stock("GOOG", 100, 490.1)
    assert stock_position.cost == 49010.0
    assert validated_add(2, 3) == 5
    assert enforced_add(3, 4) == 7

    DynamicStock = typed_structure(
        "DynamicStock",
        name=String(),
        shares=PositiveInteger(),
        price=PositiveFloat(),
    )
    assert DynamicStock("AA", 50, 25.5).name == "AA"

    portfolio_path = DATA_DIR / "portfolio.csv"
    if portfolio_path.exists():
        portfolio = reader.read_csv_as_instances(portfolio_path, stock.Stock)
        assert len(portfolio) == 7

    print("Todas las demostraciones del capítulo 7 pasaron correctamente.")


if __name__ == "__main__":
    _run_all_tests()
