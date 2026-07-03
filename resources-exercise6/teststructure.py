"""
Pruebas unitarias para structure.py (ejercicios 6.1-6.4).
"""

import unittest

from structure import Date, Structure


class TestStructure(unittest.TestCase):
    def test_date_creation_with_positional_args(self) -> None:
        current_date = Date(2026, 7, 3)
        self.assertEqual(current_date.year, 2026)
        self.assertEqual(current_date.month, 7)
        self.assertEqual(current_date.day, 3)

    def test_date_creation_with_keyword_args(self) -> None:
        current_date = Date(year=2026, month=7, day=3)
        self.assertEqual(current_date.day, 3)

    def test_date_repr(self) -> None:
        current_date = Date(2026, 7, 3)
        self.assertEqual(repr(current_date), "Date(2026, 7, 3)")

    def test_date_rejects_unknown_attribute(self) -> None:
        current_date = Date(2026, 7, 3)
        with self.assertRaises(AttributeError):
            current_date.yeear = 2025

    def test_date_allows_private_attribute(self) -> None:
        current_date = Date(2026, 7, 3)
        current_date._internal = "ok"
        self.assertEqual(current_date._internal, "ok")

    def test_date_rejects_missing_argument(self) -> None:
        with self.assertRaises(TypeError):
            Date(2026, 7)

    def test_create_init_requires_fields(self) -> None:
        class EmptyStructure(Structure):
            pass

        with self.assertRaises(ValueError):
            EmptyStructure.create_init()


if __name__ == "__main__":
    unittest.main()
