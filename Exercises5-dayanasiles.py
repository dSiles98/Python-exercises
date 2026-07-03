"""
Ejercicios 5.1 - 5.6 del curso de Python.
Autor: Dayana Siles
"""

from __future__ import annotations

import csv
import logging
import unittest
from pathlib import Path
from typing import Any, Callable, Iterable, List, Optional, Sequence, Tuple, Type, TypeVar

# ---------------------------------------------------------------------------
# Rutas de datos del curso
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).resolve().parent.parent / "python-course" / "Data"

# ---------------------------------------------------------------------------
# Ejercicio 5.1, 5.3 y 5.5 — reader.py
# ---------------------------------------------------------------------------

log = logging.getLogger(__name__)

T = TypeVar("T")


def convert_csv(
    lines: Iterable[str],
    converter: Callable[[Sequence[str], Sequence[str]], T],
    *,
    headers: Optional[Sequence[str]] = None,
) -> List[T]:
    rows = csv.reader(lines)
    if headers is None:
        headers = next(rows)

    records: List[T] = []
    for rowno, row in enumerate(rows, start=1):
        try:
            records.append(converter(headers, row))
        except ValueError as exc:
            log.warning("Row %s: Bad row: %s", rowno, row)
            log.debug("Row %s: Reason: %s", rowno, exc)
    return records


def csv_as_dicts(
    lines: Iterable[str],
    types: Sequence[Callable[[str], Any]],
    *,
    headers: Optional[Sequence[str]] = None,
) -> List[dict[str, Any]]:
    return convert_csv(
        lines,
        lambda hdrs, row: {
            name: func(val) for name, func, val in zip(hdrs, types, row)
        },
        headers=headers,
    )


def csv_as_instances(
    lines: Iterable[str],
    cls: Type[T],
    *,
    headers: Optional[Sequence[str]] = None,
) -> List[T]:
    return convert_csv(
        lines,
        lambda _hdrs, row: cls.from_row(row),
        headers=headers,
    )


def read_csv_as_dicts(
    filename: str | Path,
    types: Sequence[Callable[[str], Any]],
    *,
    headers: Optional[Sequence[str]] = None,
) -> List[dict[str, Any]]:
    with open(filename) as file:
        return csv_as_dicts(file, types, headers=headers)


def read_csv_as_instances(
    filename: str | Path,
    cls: Type[T],
    *,
    headers: Optional[Sequence[str]] = None,
) -> List[T]:
    with open(filename) as file:
        return csv_as_instances(file, cls, headers=headers)


# ---------------------------------------------------------------------------
# Ejercicio 5.2 — Devolver valores desde funciones
# ---------------------------------------------------------------------------


def parse_line(line: str) -> Optional[Tuple[str, str]]:
    if "=" not in line:
        return None
    name, value = line.split("=", maxsplit=1)
    return name, value


# ---------------------------------------------------------------------------
# Ejercicio 5.4 (a) — Closures como estructura de datos
# ---------------------------------------------------------------------------


def counter(value: int) -> Tuple[Callable[[], int], Callable[[], int]]:

    def incr() -> int:
        nonlocal value
        value += 1
        return value

    def decr() -> int:
        nonlocal value
        value -= 1
        return value

    return incr, decr


# ---------------------------------------------------------------------------
# Ejercicio 5.4 (b) y (c) — typedproperty.py con __set_name__
# ---------------------------------------------------------------------------


class TypedProperty:

    def __init__(self, expected_type: type) -> None:
        self.expected_type = expected_type
        self.name: Optional[str] = None
        self.private_name: Optional[str] = None

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name
        self.private_name = f"_{name}"

    def __get__(self, instance: Any, owner: type) -> Any:
        if instance is None:
            return self
        return getattr(instance, self.private_name)

    def __set__(self, instance: Any, value: Any) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(f"Expected {self.expected_type}")
        setattr(instance, self.private_name, value)


def String() -> TypedProperty:
    return TypedProperty(str)


def Integer() -> TypedProperty:
    return TypedProperty(int)


def Float() -> TypedProperty:
    return TypedProperty(float)


# ---------------------------------------------------------------------------
# stock.py — Clase Stock (requerida por ejercicios 5.1 y 5.6)
# ---------------------------------------------------------------------------


class Validator:

    @classmethod
    def check(cls, value: Any) -> Any:
        return value


class Typed(Validator):
    expected_type: type = object

    @classmethod
    def check(cls, value: Any) -> Any:
        if not isinstance(value, cls.expected_type):
            raise TypeError(f"Expected {cls.expected_type}")
        return super().check(value)


class IntegerValidator(Typed):
    expected_type = int


class FloatValidator(Typed):
    expected_type = float


class Positive(Validator):
    @classmethod
    def check(cls, value: Any) -> Any:
        if value < 0:
            raise ValueError("Must be >= 0")
        return super().check(value)


class PositiveInteger(IntegerValidator, Positive):
    pass


class PositiveFloat(FloatValidator, Positive):
    pass


class Stock:

    __slots__ = ("name", "_shares", "_price")
    types: Tuple[type, ...] = (str, int, float)

    def __init__(self, name: str, shares: int, price: float) -> None:
        self.name = name
        self.shares = shares
        self.price = price

    @property
    def shares(self) -> int:
        return self._shares

    @shares.setter
    def shares(self, value: int) -> None:
        self._shares = PositiveInteger.check(value)

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, value: float) -> None:
        self._price = PositiveFloat.check(value)

    @property
    def cost(self) -> float:
        return self.shares * self.price

    def sell(self, nshares: int) -> None:
        self.shares -= nshares

    @classmethod
    def from_row(cls, row: Sequence[str]) -> Stock:
        values = [func(val) for func, val in zip(cls.types, row)]
        return cls(*values)

    def __repr__(self) -> str:
        return f"Stock({self.name!r}, {self.shares!r}, {self.price!r})"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Stock)
            and (self.name, self.shares, self.price)
            == (other.name, other.shares, other.price)
        )


# ---------------------------------------------------------------------------
# Ejercicio 5.6 — teststock.py
# ---------------------------------------------------------------------------


class TestStock(unittest.TestCase):
    def test_create(self) -> None:
        s = Stock("GOOG", 100, 490.1)
        self.assertEqual(s.name, "GOOG")
        self.assertEqual(s.shares, 100)
        self.assertEqual(s.price, 490.1)

    def test_create_keyword(self) -> None:
        s = Stock(name="GOOG", shares=100, price=490.1)
        self.assertEqual(s.name, "GOOG")
        self.assertEqual(s.shares, 100)
        self.assertEqual(s.price, 490.1)

    def test_cost(self) -> None:
        s = Stock("GOOG", 100, 490.1)
        self.assertEqual(s.cost, 49010.0)

    def test_sell(self) -> None:
        s = Stock("GOOG", 100, 490.1)
        s.sell(25)
        self.assertEqual(s.shares, 75)

    def test_from_row(self) -> None:
        s = Stock.from_row(["GOOG", "100", "490.1"])
        self.assertEqual(s.name, "GOOG")
        self.assertEqual(s.shares, 100)
        self.assertEqual(s.price, 490.1)

    def test_repr(self) -> None:
        s = Stock("GOOG", 100, 490.1)
        self.assertEqual(repr(s), "Stock('GOOG', 100, 490.1)")

    def test_eq(self) -> None:
        a = Stock("GOOG", 100, 490.1)
        b = Stock("GOOG", 100, 490.1)
        self.assertTrue(a == b)

    def test_shares_badtype(self) -> None:
        s = Stock("GOOG", 100, 490.1)
        with self.assertRaises(TypeError):
            s.shares = "50"

    def test_shares_badvalue(self) -> None:
        s = Stock("GOOG", 100, 490.1)
        with self.assertRaises(ValueError):
            s.shares = -50

    def test_price_badtype(self) -> None:
        s = Stock("GOOG", 100, 490.1)
        with self.assertRaises(TypeError):
            s.price = "45.23"

    def test_price_badvalue(self) -> None:
        s = Stock("GOOG", 100, 490.1)
        with self.assertRaises(ValueError):
            s.price = -45.23

    def test_bad_attribute(self) -> None:
        s = Stock("GOOG", 100, 490.1)
        with self.assertRaises(AttributeError):
            s.share = 100


# ---------------------------------------------------------------------------
# Demostraciones rápidas
# ---------------------------------------------------------------------------


def _demo_exercises() -> None:
    portfolio_path = DATA_DIR / "portfolio.csv"
    noheader_path = DATA_DIR / "portfolio_noheader.csv"
    missing_path = DATA_DIR / "missing.csv"

    # 5.1 — lectura básica y con encabezados manuales
    port = read_csv_as_dicts(portfolio_path, [str, int, float])
    assert len(port) == 7
    assert port[0]["name"] == "AA"

    port_noheader = read_csv_as_dicts(
        noheader_path,
        [str, int, float],
        headers=["name", "shares", "price"],
    )
    assert len(port_noheader) == 7

    port_instances = read_csv_as_instances(portfolio_path, Stock)
    assert isinstance(port_instances[0], Stock)

    # 5.2 — parse_line
    assert parse_line("email=guido@python.org") == ("email", "guido@python.org")
    assert parse_line("spam") is None

    # 5.4 — counter closure
    up, down = counter(0)
    assert up() == 1 and up() == 2 and down() == 1

    # 5.5 — filas inválidas omitidas con logging
    logging.basicConfig(level=logging.WARNING)
    port_missing = read_csv_as_dicts(missing_path, [str, int, float])
    assert len(port_missing) == 20

    print("Todas las demostraciones pasaron correctamente.")


if __name__ == "__main__":
    unittest.main()
