"""
Ejercicios 4.1 - 4.4 del curso de Python.
Autor: Dayana Siles

Patrones de diseño aplicados:
- Descriptor: validadores como control del operador punto (4.3).
- Proxy: Readonly envuelve objetos de solo lectura (4.4b).
- Delegation: MySpam delega a Spam vía __getattr__ (4.4c).
- Cooperative multiple inheritance: validadores compuestos con MRO (4.2).
"""

from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from typing import Any, Optional, Sequence, Set, Tuple


# ===================================================================
# Ejercicio 4.1 — Representación de objetos e instancias
# ===================================================================


class SimpleStock:
    """Versión mínima de Stock para explorar __dict__ y el diccionario de clase."""

    def __init__(self, name: str, shares: int, price: float) -> None:
        self.name = name
        self.shares = shares
        self.price = price

    def cost(self) -> float:
        return self.shares * self.price


def demonstrate_instance_dictionary() -> dict[str, Any]:
    """Ilustra atributos de instancia vs. atributos de clase (ejercicio 4.1)."""
    google_stock = SimpleStock("GOOG", 100, 490.10)
    ibm_stock = SimpleStock("IBM", 50, 91.23)

    google_stock.date = "6/11/2007"
    google_stock.__dict__["time"] = "9:45am"
    SimpleStock.spam = 42

    return {
        "google_dict": dict(google_stock.__dict__),
        "ibm_dict": dict(ibm_stock.__dict__),
        "google_cost_via_method": google_stock.cost(),
        "google_cost_via_class_dict": SimpleStock.__dict__["cost"](google_stock),
        "class_spam_on_instance": ibm_stock.spam,
        "spam_not_in_instance_dict": "spam" not in ibm_stock.__dict__,
    }


# ===================================================================
# Ejercicio 4.2 (a) — Herencia cooperativa y MRO
# ===================================================================


class InheritanceBase:
    def spam(self) -> None:
        print("Base.spam")


class InheritanceX(InheritanceBase):
    def spam(self) -> None:
        print("X.spam")
        super().spam()


class InheritanceY(InheritanceBase):
    def spam(self) -> None:
        print("Y.spam")
        super().spam()


class InheritanceZ(InheritanceBase):
    def spam(self) -> None:
        print("Z.spam")
        super().spam()


class InheritanceM(InheritanceX, InheritanceY, InheritanceZ):
    pass


class InheritanceN(InheritanceZ, InheritanceY, InheritanceX):
    pass


class InheritanceA:
    def spam(self) -> None:
        print("A.spam")


class InheritanceB(InheritanceA):
    def spam(self) -> None:
        print("B.spam")
        super().spam()


class InheritanceC(InheritanceB):
    def spam(self) -> None:
        print("C.spam")
        super().spam()


def capture_spam_output(instance: Any) -> str:
    output_buffer = io.StringIO()
    with redirect_stdout(output_buffer):
        instance.spam()
    return output_buffer.getvalue()


# ===================================================================
# Ejercicio 4.2 (b-d) y 4.3 — validate.py con descriptors
# ===================================================================


class Validator:
    """Validador base reutilizable como @classmethod y como descriptor."""

    name: Optional[str] = None

    def __init__(self, name: Optional[str] = None) -> None:
        self.name = name

    def __set_name__(self, owner: type, attribute_name: str) -> None:
        self.name = attribute_name

    @classmethod
    def check(cls, value: Any) -> Any:
        return value

    def __set__(self, instance: Any, value: Any) -> None:
        if self.name is None:
            raise AttributeError("Validator name not set")
        instance.__dict__[self.name] = self.check(value)


class Typed(Validator):
    expected_type: type = object

    @classmethod
    def check(cls, value: Any) -> Any:
        if not isinstance(value, cls.expected_type):
            raise TypeError(f"Expected {cls.expected_type}")
        return super().check(value)


class Integer(Typed):
    expected_type = int


class Float(Typed):
    expected_type = float


class String(Typed):
    expected_type = str


class Positive(Validator):
    @classmethod
    def check(cls, value: Any) -> Any:
        if value < 0:
            raise ValueError("Must be >= 0")
        return super().check(value)


class NonEmpty(Validator):
    @classmethod
    def check(cls, value: Any) -> Any:
        if len(value) == 0:
            raise ValueError("Must be non-empty")
        return super().check(value)


class PositiveInteger(Integer, Positive):
    """Herencia cooperativa: tipo entero + valor no negativo."""


class PositiveFloat(Float, Positive):
    """Herencia cooperativa: tipo flotante + valor no negativo."""


class NonEmptyString(String, NonEmpty):
    """Herencia cooperativa: cadena no vacía."""


def validated_add(first_value: Any, second_value: Any) -> int:
    Integer.check(first_value)
    Integer.check(second_value)
    return first_value + second_value


# ===================================================================
# Ejercicio 4.3 (b) — descrip.py
# ===================================================================


class Descriptor:
    """Descriptor de demostración que intercepta get/set/delete."""

    def __init__(self, name: str) -> None:
        self.name = name

    def __get__(self, instance: Any, owner: type) -> None:
        print(f"{self.name}:__get__")

    def __set__(self, instance: Any, value: Any) -> None:
        print(f"{self.name}:__set__ {value}")

    def __delete__(self, instance: Any) -> None:
        print(f"{self.name}:__delete__")


class DescriptorDemo:
  a = Descriptor("a")
  b = Descriptor("b")
  c = Descriptor("c")


# ===================================================================
# Ejercicio 4.2 (c) — Stock con properties (versión intermedia)
# ===================================================================


class StockWithProperties:
    """Stock con validación vía properties y __slots__ (ejercicio 4.2c)."""

    __slots__ = ("name", "_shares", "_price")

    def __init__(self, name: str, shares: int, price: float) -> None:
        self.name = name
        self.shares = shares
        self.price = price

    @property
    def shares(self) -> int:
        return self._shares

    @shares.setter
    def shares(self, share_count: int) -> None:
        self._shares = PositiveInteger.check(share_count)

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, unit_price: float) -> None:
        self._price = PositiveFloat.check(unit_price)

    @property
    def cost(self) -> float:
        return self.shares * self.price

    def sell(self, share_count: int) -> None:
        self.shares -= share_count

    def __repr__(self) -> str:
        return f"Stock({self.name!r}, {self.shares!r}, {self.price!r})"


# ===================================================================
# Ejercicio 4.3 (d) y 4.4 (a) — Stock con descriptors y __setattr__
# ===================================================================


class Stock:
    """
    Stock con validadores como descriptors y restricción de atributos.
    Patrón: Descriptor + validación declarativa en la clase.
    """

    _allowed_attributes: Set[str] = {"name", "shares", "price"}
    _types: Tuple[type, ...] = (str, int, float)

    name = NonEmptyString()
    shares = PositiveInteger()
    price = PositiveFloat()

    def __init__(self, name: str, shares: int, price: float) -> None:
        self.name = name
        self.shares = shares
        self.price = price

    def __setattr__(self, attribute_name: str, attribute_value: Any) -> None:
        if attribute_name not in self._allowed_attributes:
            raise AttributeError(f"No attribute {attribute_name}")
        super().__setattr__(attribute_name, attribute_value)

    @property
    def cost(self) -> float:
        return self.shares * self.price

    def sell(self, share_count: int) -> None:
        self.shares -= share_count

    @classmethod
    def from_row(cls, row: Sequence[str]) -> Stock:
        converted_values = [
            converter(raw_value)
            for converter, raw_value in zip(cls._types, row)
        ]
        return cls(*converted_values)

    def __repr__(self) -> str:
        return f"Stock({self.name!r}, {self.shares!r}, {self.price!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Stock):
            return NotImplemented
        return (self.name, self.shares, self.price) == (
            other.name,
            other.shares,
            other.price,
        )


# ===================================================================
# Ejercicio 4.4 (b) — Proxy de solo lectura
# ===================================================================


class Readonly:
    """
    Proxy de solo lectura. Patrón: Proxy.
    Delega lecturas al objeto envuelto y rechaza escrituras.
    """

    def __init__(self, wrapped_object: Any) -> None:
        self.__dict__["_wrapped_object"] = wrapped_object

    def __setattr__(self, attribute_name: str, attribute_value: Any) -> None:
        raise AttributeError("Can't set attribute")

    def __getattr__(self, attribute_name: str) -> Any:
        return getattr(self._wrapped_object, attribute_name)


# ===================================================================
# Ejercicio 4.4 (c) — Delegación como alternativa a herencia
# ===================================================================


class Spam:
    def a(self) -> None:
        print("Spam.a")

    def b(self) -> None:
        print("Spam.b")


class MySpam:
    """
    Envuelve Spam y redefine métodos selectivamente.
    Patrón: Delegation vía __getattr__.
    """

    def __init__(self) -> None:
        self._spam = Spam()

    def a(self) -> None:
        print("MySpam.a")
        self._spam.a()

    def c(self) -> None:
        print("MySpam.c")

    def __getattr__(self, attribute_name: str) -> Any:
        return getattr(self._spam, attribute_name)


# ===================================================================
# Pruebas unitarias
# ===================================================================


class TestSimpleStockModel(unittest.TestCase):
    def test_instance_and_class_attribute_behavior(self) -> None:
        results = demonstrate_instance_dictionary()
        self.assertEqual(results["google_cost_via_method"], 49010.0)
        self.assertEqual(results["google_cost_via_class_dict"], 49010.0)
        self.assertEqual(results["class_spam_on_instance"], 42)
        self.assertTrue(results["spam_not_in_instance_dict"])
        self.assertIn("date", results["google_dict"])
        self.assertEqual(results["google_dict"]["time"], "9:45am")
        self.assertNotIn("date", results["ibm_dict"])


class TestInheritanceMRO(unittest.TestCase):
    def test_linear_inheritance_mro(self) -> None:
        self.assertEqual(
            InheritanceC.__mro__,
            (InheritanceC, InheritanceB, InheritanceA, object),
        )
        output = capture_spam_output(InheritanceC())
        self.assertEqual(output.splitlines(), ["C.spam", "B.spam", "A.spam"])

    def test_diamond_inheritance_order_depends_on_subclass(self) -> None:
        output_m = capture_spam_output(InheritanceM())
        self.assertEqual(
            output_m.splitlines(),
            ["X.spam", "Y.spam", "Z.spam", "Base.spam"],
        )

        output_n = capture_spam_output(InheritanceN())
        self.assertEqual(
            output_n.splitlines(),
            ["Z.spam", "Y.spam", "X.spam", "Base.spam"],
        )


class TestValidators(unittest.TestCase):
    def test_integer_accepts_int_rejects_str(self) -> None:
        self.assertEqual(Integer.check(10), 10)
        with self.assertRaises(TypeError):
            Integer.check("10")

    def test_positive_integer_rejects_negative(self) -> None:
        self.assertEqual(PositiveInteger.check(10), 10)
        with self.assertRaises(ValueError):
            PositiveInteger.check(-10)

    def test_nonempty_string_rejects_empty(self) -> None:
        self.assertEqual(NonEmptyString.check("hello"), "hello")
        with self.assertRaises(ValueError):
            NonEmptyString.check("")

    def test_validated_add(self) -> None:
        self.assertEqual(validated_add(2, 2), 4)
        with self.assertRaises(TypeError):
            validated_add("2", "3")


class TestDescriptorProtocol(unittest.TestCase):
    def test_descriptor_intercepts_attribute_access(self) -> None:
        demo_object = DescriptorDemo()
        output_buffer = io.StringIO()

        with redirect_stdout(output_buffer):
            demo_object.a
            demo_object.b
            demo_object.a = 23
            del demo_object.a

        lines = output_buffer.getvalue().splitlines()
        self.assertEqual(lines[0], "a:__get__")
        self.assertEqual(lines[1], "b:__get__")
        self.assertEqual(lines[2], "a:__set__ 23")
        self.assertEqual(lines[3], "a:__delete__")

    def test_stock_descriptor_set_and_get(self) -> None:
        stock_position = Stock("GOOG", 100, 490.10)
        shares_descriptor = Stock.__dict__["shares"]
        # Sin __get__ en el descriptor, el valor vive en instance.__dict__
        self.assertEqual(stock_position.__dict__["shares"], 100)
        shares_descriptor.__set__(stock_position, 75)
        self.assertEqual(stock_position.shares, 75)
        with self.assertRaises(TypeError):
            shares_descriptor.__set__(stock_position, "75")


class TestStock(unittest.TestCase):
    def test_create_and_cost(self) -> None:
        stock_position = Stock("GOOG", 100, 490.1)
        self.assertEqual(stock_position.name, "GOOG")
        self.assertEqual(stock_position.cost, 49010.0)

    def test_sell_updates_shares(self) -> None:
        stock_position = Stock("GOOG", 100, 490.1)
        stock_position.sell(25)
        self.assertEqual(stock_position.shares, 75)

    def test_shares_rejects_invalid_values(self) -> None:
        stock_position = Stock("GOOG", 100, 490.1)
        with self.assertRaises(TypeError):
            stock_position.shares = "50"
        with self.assertRaises(ValueError):
            stock_position.shares = -50

    def test_price_rejects_invalid_values(self) -> None:
        stock_position = Stock("GOOG", 100, 490.1)
        with self.assertRaises(TypeError):
            stock_position.price = "45.23"
        with self.assertRaises(ValueError):
            stock_position.price = -45.23

    def test_setattr_restricts_unknown_attributes(self) -> None:
        stock_position = Stock("GOOG", 100, 490.1)
        with self.assertRaises(AttributeError):
            stock_position.share = 100

    def test_from_row_and_repr(self) -> None:
        stock_position = Stock.from_row(["GOOG", "100", "490.1"])
        self.assertEqual(repr(stock_position), "Stock('GOOG', 100, 490.1)")

    def test_equality(self) -> None:
        first = Stock("GOOG", 100, 490.1)
        second = Stock("GOOG", 100, 490.1)
        self.assertTrue(first == second)


class TestStockWithProperties(unittest.TestCase):
    def test_property_based_validation(self) -> None:
        stock_position = StockWithProperties("GOOG", 100, 490.1)
        with self.assertRaises(ValueError):
            stock_position.shares = -1


class TestProxyAndDelegation(unittest.TestCase):
    def test_readonly_proxy_blocks_writes(self) -> None:
        stock_position = Stock("GOOG", 100, 490.1)
        readonly_position = Readonly(stock_position)
        self.assertEqual(readonly_position.name, "GOOG")
        self.assertEqual(readonly_position.cost, 49010.0)
        with self.assertRaises(AttributeError):
            readonly_position.shares = 50

    def test_myspam_delegates_unimplemented_methods(self) -> None:
        delegated_spam = MySpam()
        output_buffer = io.StringIO()

        with redirect_stdout(output_buffer):
            delegated_spam.a()
            delegated_spam.b()
            delegated_spam.c()

        self.assertEqual(
            output_buffer.getvalue().splitlines(),
            ["MySpam.a", "Spam.a", "Spam.b", "MySpam.c"],
        )


def _demo_exercises() -> None:
    demonstrate_instance_dictionary()
    assert validated_add(2, 3) == 5
    stock_position = Stock("GOOG", 100, 490.1)
    assert stock_position.cost == 49010.0
    readonly_position = Readonly(stock_position)
    assert readonly_position.shares == 100
    print("Todas las demostraciones del capítulo 4 pasaron correctamente.")


if __name__ == "__main__":
    unittest.main()
