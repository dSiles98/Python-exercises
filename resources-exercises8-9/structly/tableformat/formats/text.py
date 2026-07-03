"""Formateador de tabla en texto plano."""

from __future__ import annotations

from typing import Any, Sequence

from ..formatter import TableFormatter


class TextTableFormatter(TableFormatter):
    def headings(self, headers: Sequence[str]) -> None:
        print(" ".join(f"{header:>10s}" for header in headers))
        print(("-" * 10 + " ") * len(headers))

    def row(self, row_data: Sequence[Any]) -> None:
        print(" ".join(f"{str(value):>10s}" for value in row_data))
