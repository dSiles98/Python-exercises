"""
Clase Stock con validators inyectados por metaclase (ejercicios 7.3 y 7.6).
"""

from __future__ import annotations

from structure import Structure


class Stock(Structure):
    """
    Acción en un portafolio.
    Los tipos String, PositiveInteger y PositiveFloat están disponibles
    automáticamente vía StructureMeta (sin importarlos explícitamente).
    """

    name = String()
    shares = PositiveInteger()
    price = PositiveFloat()

    @property
    def cost(self) -> float:
        return self.shares * self.price

    def sell(self, share_count: PositiveInteger) -> None:
        self.shares -= share_count
