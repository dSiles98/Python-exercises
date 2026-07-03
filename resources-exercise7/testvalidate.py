"""
Pruebas unitarias para validate.py (ejercicios 6.5 y 7.x).
"""

import unittest

from validate import Integer, PositiveInteger, enforce, validated


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

        with self.assertRaises(TypeError) as error_context:
            add("two", "three")

        error_message = str(error_context.exception)
        self.assertIn("Bad Arguments", error_message)
        self.assertIn("x", error_message.lower() or "first")

    def test_return_value_is_validated(self) -> None:
        @validated
        def broken_add(first: Integer, second: Integer) -> Integer:
            return "not an int"

        with self.assertRaises(TypeError) as error_context:
            broken_add(1, 2)

        self.assertIn("Bad return", str(error_context.exception))

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

        with self.assertRaises(TypeError) as error_context:
            portfolio.withdraw(-10)

        self.assertIn("Bad Arguments", str(error_context.exception))

    def test_enforce_decorator(self) -> None:
        @enforce(x=Integer, y=Integer, return_=Integer)
        def add(x: int, y: int) -> int:
            return x + y

        self.assertEqual(add(2, 3), 5)

        with self.assertRaises(TypeError):
            add("2", "3")

    def test_pow_validates_return(self) -> None:
        @validated
        def pow_int(base: Integer, exponent: Integer) -> Integer:
            return base**exponent

        self.assertEqual(pow_int(2, 3), 8)

        with self.assertRaises(TypeError) as error_context:
            pow_int(2, -1)

        self.assertIn("Bad return", str(error_context.exception))


if __name__ == "__main__":
    unittest.main()
