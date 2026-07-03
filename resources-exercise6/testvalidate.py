"""
Pruebas unitarias para validate.py (ejercicio 6.5).
"""

import unittest

from validate import Integer, PositiveInteger, validated


class TestValidatedFunction(unittest.TestCase):
    def test_valid_arguments_pass(self) -> None:
        @validated
        def add(first: Integer, second: Integer) -> Integer:
            return first + second

        self.assertEqual(add(2, 3), 5)

    def test_invalid_arguments_raise_type_error(self) -> None:
        @validated
        def add(first: Integer, second: Integer) -> Integer:
            return first + second

        with self.assertRaises(TypeError):
            add("two", "three")

    def test_return_value_is_validated(self) -> None:
        @validated
        def broken_add(first: Integer, second: Integer) -> Integer:
            return "not an int"

        with self.assertRaises(TypeError):
            broken_add(1, 2)

    def test_works_as_bound_method(self) -> None:
        class Portfolio:
            def __init__(self) -> None:
                self.balance = 100

            @validated
            def withdraw(self, amount: PositiveInteger) -> None:
                self.balance -= amount

        portfolio = Portfolio()
        portfolio.withdraw(30)
        self.assertEqual(portfolio.balance, 70)

        with self.assertRaises(ValueError):
            portfolio.withdraw(-10)


if __name__ == "__main__":
    unittest.main()
