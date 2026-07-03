"""
Lectura de archivos CSV (ejercicios 5.x, usado en 7.6).
"""

from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Any, Callable, Iterable, List, Optional, Sequence, Type, TypeVar

log = logging.getLogger(__name__)

T = TypeVar("T")


def convert_csv(
    lines: Iterable[str],
    converter: Callable[[Sequence[str], Sequence[str]], T],
    *,
    headers: Optional[Sequence[str]] = None,
) -> List[T]:
    rows = csv.reader(lines)
    if headers is None:
        headers = next(rows)

    records: List[T] = []
    for row_number, row in enumerate(rows, start=1):
        try:
            records.append(converter(headers, row))
        except ValueError as exc:
            log.warning("Row %s: Bad row: %s", row_number, row)
            log.debug("Row %s: Reason: %s", row_number, exc)
    return records


def csv_as_dicts(
    lines: Iterable[str],
    types: Sequence[Callable[[str], Any]],
    *,
    headers: Optional[Sequence[str]] = None,
) -> List[dict[str, Any]]:
    return convert_csv(
        lines,
        lambda column_headers, row: {
            column_name: type_converter(cell_value)
            for column_name, type_converter, cell_value in zip(
                column_headers, types, row
            )
        },
        headers=headers,
    )


def csv_as_instances(
    lines: Iterable[str],
    instance_class: Type[T],
    *,
    headers: Optional[Sequence[str]] = None,
) -> List[T]:
    return convert_csv(
        lines,
        lambda _column_headers, row: instance_class.from_row(row),
        headers=headers,
    )


def read_csv_as_dicts(
    filename: str | Path,
    types: Sequence[Callable[[str], Any]],
    *,
    headers: Optional[Sequence[str]] = None,
) -> List[dict[str, Any]]:
    with open(filename) as csv_file:
        return csv_as_dicts(csv_file, types, headers=headers)


def read_csv_as_instances(
    filename: str | Path,
    instance_class: Type[T],
    *,
    headers: Optional[Sequence[str]] = None,
) -> List[T]:
    with open(filename) as csv_file:
        return csv_as_instances(csv_file, instance_class, headers=headers)
