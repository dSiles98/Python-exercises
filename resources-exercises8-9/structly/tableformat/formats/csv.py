"""Formateador de tabla en CSV."""

from __future__ import annotations

from typing import Any, Sequence

from ..formatter import TableFormatter


class CSVTableFormatter(TableFormatter):
    def headings(self, headers: Sequence[str]) -> None:
        print(",".join(headers))

    def row(self, row_data: Sequence[Any]) -> None:
        print(",".join(str(value) for value in row_data))
