"""
Clase Stock construida sobre Structure (ejercicios 6.1-6.4).
"""

from __future__ import annotations

from typing import Sequence, Tuple

from structure import Structure
from validate import PositiveFloat, PositiveInteger


class Stock(Structure):
    """Acción en un portafolio."""

    _fields = ("name", "shares", "price")
    _types: Tuple[type, ...] = (str, int, float)

    @property
    def shares(self) -> int:
        return self._shares

    @shares.setter
    def shares(self, share_count: int) -> None:
        validated_count = PositiveInteger.check(share_count)
        self._shares = validated_count

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, unit_price: float) -> None:
        validated_price = PositiveFloat.check(unit_price)
        self._price = validated_price

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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Stock):
            return NotImplemented
        return (self.name, self.shares, self.price) == (
            other.name,
            other.shares,
            other.price,
        )


Stock.create_init()
