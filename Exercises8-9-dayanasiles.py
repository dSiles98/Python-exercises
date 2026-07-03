"""
Ejercicios 8.1 - 9.4 del curso de Python.
Autor: Dayana Siles
"""

from __future__ import annotations

import importlib
import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Generator
from unittest import mock

DATA_DIR = Path(__file__).resolve().parent.parent / "python-course" / "Data"
EXERCISES_DIR = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# Capítulo 8 — Generadores, coroutines y async
# ---------------------------------------------------------------------------


class TestGenerators(unittest.TestCase):
    def test_frange_values(self) -> None:
        from follow import frange

        values = list(frange(0, 1, 0.25))
        self.assertEqual(values, [0.0, 0.25, 0.5, 0.75])

    def test_fractional_range_reusable(self) -> None:
        from follow import FractionalRange

        fractional_range = FractionalRange(0, 1, 0.5)
        self.assertEqual(list(fractional_range), [0.0, 0.5])
        self.assertEqual(list(fractional_range), [0.0, 0.5])

    @mock.patch("follow.time.sleep")
    def test_follow_yields_when_readline_returns_data(self, mock_sleep: mock.Mock) -> None:
        from follow import follow

        mock_file_handle = mock.mock_open()
        mock_file_handle.return_value.readline.side_effect = ["data\n", "", ""]

        with mock.patch("follow.open", mock_file_handle):
            line_generator = follow("fake.csv")
            self.assertEqual(next(line_generator), "data\n")
            line_generator.close()
        mock_sleep.assert_not_called()

    def test_follow_handles_generator_exit(self) -> None:
        from follow import follow

        mock_file_handle = mock.mock_open()
        mock_file_handle.return_value.readline.side_effect = ["line\n", StopIteration]

        with mock.patch("follow.open", mock_file_handle):
            output_buffer = io.StringIO()
            line_generator = follow("fake.csv")
            next(line_generator)
            with redirect_stdout(output_buffer):
                line_generator.close()

        self.assertIn("Following Done", output_buffer.getvalue())


class TestCoroutines(unittest.TestCase):
    def test_printer_receives_messages(self) -> None:
        from cofollow import printer

        output_buffer = io.StringIO()
        message_printer = printer()
        with redirect_stdout(output_buffer):
            message_printer.send("hello")
            message_printer.send(42)
        self.assertIn("hello", output_buffer.getvalue())

    def test_printer_handles_thrown_exceptions(self) -> None:
        from cofollow import printer

        output_buffer = io.StringIO()
        message_printer = printer()
        with redirect_stdout(output_buffer):
            message_printer.throw(ValueError("It failed"))
        self.assertIn("ERROR:", output_buffer.getvalue())

    def test_receive_validates_message_type(self) -> None:
        from cofollow import consumer, receive

        @consumer
        def print_integers() -> Generator[None, object, None]:
            while True:
                value = yield from receive(int)
                print(value)

        output_buffer = io.StringIO()
        integer_printer = print_integers()
        with redirect_stdout(output_buffer):
            integer_printer.send(42)
            with self.assertRaises(AssertionError):
                integer_printer.send("13")
        self.assertIn("42", output_buffer.getvalue())


class TestMultitask(unittest.TestCase):
    def test_countdown_completes(self) -> None:
        import multitask

        output_buffer = io.StringIO()
        with redirect_stdout(output_buffer):
            multitask.tasks.clear()
            multitask.tasks.append(multitask.countdown(3))
            multitask.run()
        self.assertIn("T-minus 1", output_buffer.getvalue())
        self.assertIn("Task done", output_buffer.getvalue())


class TestTickerPipeline(unittest.TestCase):
    def test_ticker_from_row(self) -> None:
        from ticker import Ticker

        ticker_record = Ticker.from_row(
            ["IBM", "103.53", "6/11/2007", "09:53.59", "0.46", "102.87", "103.53", "102.77", "541633"]
        )
        self.assertEqual(ticker_record.name, "IBM")
        self.assertAlmostEqual(ticker_record.price, 103.53)


# ---------------------------------------------------------------------------
# Capítulo 9 — Módulos y paquetes
# ---------------------------------------------------------------------------


class TestSimpleMod(unittest.TestCase):
    def test_import_and_call(self) -> None:
        if "simplemod" in sys.modules:
            del sys.modules["simplemod"]

        import simplemod

        output_buffer = io.StringIO()
        with redirect_stdout(output_buffer):
            simplemod.foo()
        self.assertIn("x is 42", output_buffer.getvalue())

    def test_reload_restores_original_value(self) -> None:
        import simplemod

        simplemod.x = 13
        reloaded_module = importlib.reload(simplemod)
        self.assertEqual(reloaded_module.x, 42)


class TestStructlyPackage(unittest.TestCase):
    def test_package_exports_structure(self) -> None:
        import structly

        self.assertTrue(hasattr(structly, "Structure"))
        self.assertTrue(hasattr(structly, "read_csv_as_instances"))
        self.assertTrue(hasattr(structly, "create_formatter"))
        self.assertTrue(hasattr(structly, "String"))

    def test_formatter_registry_dynamic_import(self) -> None:
        from structly.tableformat.formatter import TableFormatter, create_formatter

        original_registry = dict(TableFormatter._formats)
        try:
            TableFormatter._formats.clear()
            text_formatter = create_formatter("text")
            self.assertEqual(text_formatter.__class__.__module__.split(".")[-1], "text")
            self.assertIn("text", TableFormatter._formats)
        finally:
            TableFormatter._formats.clear()
            TableFormatter._formats.update(original_registry)

    def test_stock_reads_portfolio(self) -> None:
        portfolio_path = DATA_DIR / "portfolio.csv"
        if not portfolio_path.exists():
            self.skipTest("portfolio.csv no disponible")

        import stock

        portfolio = stock.read_csv_as_instances(portfolio_path, stock.Stock)
        self.assertEqual(len(portfolio), 7)
        self.assertEqual(portfolio[0].name, "AA")

    def test_stock_main_script(self) -> None:
        portfolio_path = DATA_DIR / "portfolio.csv"
        if not portfolio_path.exists():
            self.skipTest("portfolio.csv no disponible")

        output_buffer = io.StringIO()
        with mock.patch("sys.argv", ["stock.py"]):
            with redirect_stdout(output_buffer):
                import runpy

                runpy.run_path(str(EXERCISES_DIR / "stock.py"), run_name="__main__")
        self.assertIn("AA", output_buffer.getvalue())


class TestGenSocket(unittest.TestCase):
    def test_gen_socket_delegates_attributes(self) -> None:
        from server import GenSocket

        mock_socket = mock.Mock()
        mock_socket.getsockname.return_value = ("127.0.0.1", 25000)
        wrapped_socket = GenSocket(mock_socket)
        self.assertEqual(wrapped_socket.getsockname(), ("127.0.0.1", 25000))


def _run_all_tests(verbosity: int = 2) -> unittest.TestResult:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for module_name in ("teststock", "teststructure"):
        suite.addTests(loader.loadTestsFromModule(importlib.import_module(module_name)))
    suite.addTests(loader.loadTestsFromTestCase(TestGenerators))
    suite.addTests(loader.loadTestsFromTestCase(TestCoroutines))
    suite.addTests(loader.loadTestsFromTestCase(TestMultitask))
    suite.addTests(loader.loadTestsFromTestCase(TestTickerPipeline))
    suite.addTests(loader.loadTestsFromTestCase(TestSimpleMod))
    suite.addTests(loader.loadTestsFromTestCase(TestStructlyPackage))
    suite.addTests(loader.loadTestsFromTestCase(TestGenSocket))
    return unittest.TextTestRunner(verbosity=verbosity).run(suite)


def _demo_exercises() -> None:
    import stock
    from follow import frange
    from structly import create_formatter, read_csv_as_instances, typed_structure
    from structly.validate import PositiveFloat, PositiveInteger, String

    stock_position = stock.Stock("GOOG", 100, 490.1)
    assert list(stock_position) == ["GOOG", 100, 490.1]
    assert list(frange(0, 1, 0.5)) == [0.0, 0.5]

    DynamicStock = typed_structure(
        "DynamicStock",
        name=String(),
        shares=PositiveInteger(),
        price=PositiveFloat(),
    )
    assert DynamicStock("AA", 10, 20.5).name == "AA"

    portfolio_path = DATA_DIR / "portfolio.csv"
    if portfolio_path.exists():
        portfolio = read_csv_as_instances(portfolio_path, stock.Stock)
        assert len(portfolio) == 7

    print("Todas las demostraciones de los capítulos 8-9 pasaron correctamente.")


if __name__ == "__main__":
    _run_all_tests()
