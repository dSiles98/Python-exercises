"""Formateador de tabla en HTML."""

from __future__ import annotations

from typing import Any, Sequence

from ..formatter import TableFormatter


class HTMLTableFormatter(TableFormatter):
    def headings(self, headers: Sequence[str]) -> None:
        print("<tr>", end=" ")
        for header in headers:
            print(f"<th>{header}</th>", end=" ")
        print("</tr>")

    def row(self, row_data: Sequence[Any]) -> None:
        print("<tr>", end=" ")
        for value in row_data:
            print(f"<td>{value}</td>", end=" ")
        print("</tr>")
