"""Clases base y factory de formateadores de tabla."""

from __future__ import annotations

import importlib
from abc import ABC, abstractmethod
from typing import Any, Iterable, Sequence


def print_table(
    records: Iterable[Any],
    fields: Sequence[str],
    formatter: TableFormatter,
) -> None:
    if not isinstance(formatter, TableFormatter):
        raise RuntimeError("Expected a TableFormatter")

    formatter.headings(fields)
    for record in records:
        row_data = [getattr(record, field_name) for field_name in fields]
        formatter.row(row_data)


class TableFormatter(ABC):
    _formats: dict[str, type[TableFormatter]] = {}

    @classmethod
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        format_name = cls.__module__.split(".")[-1]
        TableFormatter._formats[format_name] = cls

    @abstractmethod
    def headings(self, headers: Sequence[str]) -> None:
        pass

    @abstractmethod
    def row(self, row_data: Sequence[Any]) -> None:
        pass


class ColumnFormatMixin:
    formats: list[str] = []

    def row(self, row_data: Sequence[Any]) -> None:
        formatted_row = [
            format_string % item
            for format_string, item in zip(self.formats, row_data)
        ]
        super().row(formatted_row)


class UpperHeadersMixin:
    def headings(self, headers: Sequence[str]) -> None:
        super().headings([header.upper() for header in headers])


def _ensure_format_registered(format_name: str) -> None:
    """Registra un formateador por nombre, incluso si el módulo ya fue importado."""
    if format_name in TableFormatter._formats:
        return

    format_module = importlib.import_module(f"{__package__}.formats.{format_name}")
    for attribute_value in vars(format_module).values():
        if (
            isinstance(attribute_value, type)
            and issubclass(attribute_value, TableFormatter)
            and attribute_value is not TableFormatter
        ):
            TableFormatter._formats.setdefault(format_name, attribute_value)
            return

    raise RuntimeError(f"Unknown format {format_name}")


def create_formatter(
    format_name: str,
    column_formats: list[str] | None = None,
    upper_headers: bool = False,
) -> TableFormatter:
    _ensure_format_registered(format_name)

    formatter_class = TableFormatter._formats.get(format_name)
    if formatter_class is None:
        raise RuntimeError(f"Unknown format {format_name}")

    selected_class = formatter_class

    if column_formats:
        class FormattedClass(ColumnFormatMixin, selected_class):
            formats = column_formats

        selected_class = FormattedClass

    if upper_headers:
        class UpperClass(UpperHeadersMixin, selected_class):
            pass

        selected_class = UpperClass

    return selected_class()
