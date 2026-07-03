"""
Pruebas unitarias para stock.py (ejercicios 5.6 y 6.x).
"""

import unittest

import stock
from validate import PositiveInteger, validated


class TestStock(unittest.TestCase):
    def test_create(self) -> None:
        stock_position = stock.Stock("GOOG", 100, 490.1)
        self.assertEqual(stock_position.name, "GOOG")
        self.assertEqual(stock_position.shares, 100)
        self.assertEqual(stock_position.price, 490.1)

    def test_create_keyword(self) -> None:
        stock_position = stock.Stock(name="GOOG", shares=100, price=490.1)
        self.assertEqual(stock_position.name, "GOOG")
        self.assertEqual(stock_position.shares, 100)
        self.assertEqual(stock_position.price, 490.1)

    def test_cost(self) -> None:
        stock_position = stock.Stock("GOOG", 100, 490.1)
        self.assertEqual(stock_position.cost, 49010.0)

    def test_sell(self) -> None:
        stock_position = stock.Stock("GOOG", 100, 490.1)
        stock_position.sell(25)
        self.assertEqual(stock_position.shares, 75)

    def test_from_row(self) -> None:
        stock_position = stock.Stock.from_row(["GOOG", "100", "490.1"])
        self.assertEqual(stock_position.name, "GOOG")
        self.assertEqual(stock_position.shares, 100)
        self.assertEqual(stock_position.price, 490.1)

    def test_repr(self) -> None:
        stock_position = stock.Stock("GOOG", 100, 490.1)
        self.assertEqual(repr(stock_position), "Stock('GOOG', 100, 490.1)")

    def test_eq(self) -> None:
        first_position = stock.Stock("GOOG", 100, 490.1)
        second_position = stock.Stock("GOOG", 100, 490.1)
        self.assertTrue(first_position == second_position)

    def test_shares_badtype(self) -> None:
        stock_position = stock.Stock("GOOG", 100, 490.1)
        with self.assertRaises(TypeError):
            stock_position.shares = "50"

    def test_shares_badvalue(self) -> None:
        stock_position = stock.Stock("GOOG", 100, 490.1)
        with self.assertRaises(ValueError):
            stock_position.shares = -50

    def test_price_badtype(self) -> None:
        stock_position = stock.Stock("GOOG", 100, 490.1)
        with self.assertRaises(TypeError):
            stock_position.price = "45.23"

    def test_price_badvalue(self) -> None:
        stock_position = stock.Stock("GOOG", 100, 490.1)
        with self.assertRaises(ValueError):
            stock_position.price = -45.23

    def test_bad_attribute(self) -> None:
        stock_position = stock.Stock("GOOG", 100, 490.1)
        with self.assertRaises(AttributeError):
            stock_position.share = 100

    def test_validated_sell_method(self) -> None:
        class ValidatedStock(stock.Stock):
            @validated
            def sell(self, share_count: PositiveInteger) -> None:
                self.shares -= share_count

        stock_position = ValidatedStock("GOOG", 100, 490.1)
        stock_position.sell(10)
        self.assertEqual(stock_position.shares, 90)

        with self.assertRaises(TypeError):
            stock_position.sell("ten")


if __name__ == "__main__":
    unittest.main()
