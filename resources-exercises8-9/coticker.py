"""
Pipeline con coroutines para ticker bursátil (ejercicios 8.3 y 8.6).
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Generator, List

from cofollow import consumer, follow, receive
from structly import Float, Integer, String, Structure, create_formatter


class Ticker(Structure):
    name = String()
    price = Float()
    date = String()
    time = String()
    change = Float()
    open = Float()
    high = Float()
    low = Float()
    volume = Integer()


@consumer
def to_csv(target: Generator[Any, Any, Any]) -> Generator[None, Any, None]:
    current_line = ""

    def line_producer() -> Generator[str, None, None]:
        nonlocal current_line
        while True:
            yield current_line

    csv_reader = csv.reader(line_producer())
    while True:
        current_line = yield from receive(str)
        target.send(next(csv_reader))


@consumer
def create_ticker(target: Generator[Any, Any, Any]) -> Generator[None, Any, None]:
    while True:
        csv_row = yield from receive(list)
        target.send(Ticker.from_row(csv_row))


@consumer
def negchange(target: Generator[Any, Any, Any]) -> Generator[None, Any, None]:
    while True:
        ticker_record = yield from receive(Ticker)
        if ticker_record.change < 0:
            target.send(ticker_record)


@consumer
def ticker_sink(
    format_name: str, display_fields: List[str]
) -> Generator[None, Any, None]:
    formatter = create_formatter(format_name)
    formatter.headings(display_fields)
    while True:
        ticker_record = yield from receive(Ticker)
        row_data = [getattr(ticker_record, field_name) for field_name in display_fields]
        formatter.row(row_data)


if __name__ == "__main__":
    data_dir = Path(__file__).resolve().parent.parent / "python-course" / "Data"
    log_path = data_dir / "stocklog.csv"
    display_fields = ["name", "price", "change"]

    follow(
        log_path,
        to_csv(
            create_ticker(
                negchange(
                    ticker_sink("text", display_fields)
                )
            )
        ),
    )
