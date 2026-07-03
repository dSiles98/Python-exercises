"""
Clase Stock usando el paquete structly (ejercicios 9.2-9.3).
"""

from __future__ import annotations

from structly import *


class Stock(Structure):
    name = String()
    shares = PositiveInteger()
    price = PositiveFloat()

    @property
    def cost(self) -> float:
        return self.shares * self.price

    def sell(self, share_count: PositiveInteger) -> None:
        self.shares -= share_count


if __name__ == "__main__":
    from pathlib import Path

    portfolio_path = Path(__file__).resolve().parent.parent / "python-course" / "Data" / "portfolio.csv"
    portfolio = read_csv_as_instances(portfolio_path, Stock)
    formatter = create_formatter("text")
    print_table(portfolio, ["name", "shares", "price"], formatter)
