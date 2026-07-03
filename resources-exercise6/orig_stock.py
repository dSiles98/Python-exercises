"""
Respaldo de la implementación de Stock previa al ejercicio 6.1.
"""

from __future__ import annotations

from typing import Sequence, Tuple

from validate import PositiveFloat, PositiveInteger


class Stock:
    """Implementación original con __slots__ y properties (pre-Structure)."""

    __slots__ = ("name", "_shares", "_price")
    _types: Tuple[type, ...] = (str, int, float)

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
