"""
Pruebas unitarias para structure.py y structly.
"""

import unittest

from structly.structure import Date, Structure, typed_structure
from structly.validate import Float, PositiveFloat, PositiveInteger, String


class TestStructure(unittest.TestCase):
    def test_date_creation(self) -> None:
        current_date = Date(2026, 7, 3)
        self.assertEqual(repr(current_date), "Date(2026, 7, 3)")

    def test_date_rejects_unknown_attribute(self) -> None:
        current_date = Date(2026, 7, 3)
        with self.assertRaises(AttributeError):
            current_date.yeear = 2025

    def test_typed_structure_factory(self) -> None:
        DynamicStock = typed_structure(
            "DynamicStock",
            name=String(),
            shares=PositiveInteger(),
            price=PositiveFloat(),
        )
        position = DynamicStock("GOOG", 100, 490.1)
        self.assertEqual(position.name, "GOOG")
        self.assertEqual(list(position), ["GOOG", 100, 490.1])


if __name__ == "__main__":
    unittest.main()
