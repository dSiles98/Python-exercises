"""
Ejercicios 2.1 - 2.6 del curso de Python.
Autor: Dayana Siles

Patrones de diseño aplicados:
- Strategy: distintas representaciones de filas (tuplas, dicts, slots) intercambiables (2.1).
- Facade / Data abstraction: RideData y DataCollection ocultan almacenamiento columnar (2.5, 2.6).
- Sequence protocol: __len__ y __getitem__ para compatibilidad con código existente (2.5).
- First-class functions: conversiones de tipo como callables en reader (2.6).
"""

from __future__ import annotations

import collections.abc
import csv
import io
import sys
import tracemalloc
import unittest
from collections import Counter, defaultdict, namedtuple
from contextlib import redirect_stdout
from functools import total_ordering
from pathlib import Path
from typing import Any, Callable, Iterator, Mapping, Sequence

# ---------------------------------------------------------------------------
# Rutas de datos del curso
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).resolve().parent.parent / "python-course" / "Data"
PORTFOLIO_CSV = DATA_DIR / "portfolio.csv"
CTABUS_CSV = DATA_DIR / "ctabus.csv"

ColumnConverter = Callable[[str], Any]
PortfolioRecord = dict[str, Any]
BusRideRecord = dict[str, Any]


# ===================================================================
# Ejercicio 2.1 — readrides.py: representaciones y memoria
# ===================================================================


BusRideTuple = tuple[str, str, str, int]
BusRideNamedTuple = namedtuple("BusRideNamedTuple", ["route", "date", "daytype", "rides"])


class BusRideRow:
    """Fila de viaje como instancia de clase estándar."""

    def __init__(self, route: str, date: str, daytype: str, rides: int) -> None:
        self.route = route
        self.date = date
        self.daytype = daytype
        self.rides = rides


class BusRideSlotsRow:
    """Fila de viaje con __slots__ para menor huella de memoria."""

    __slots__ = ("route", "date", "daytype", "rides")

    def __init__(self, route: str, date: str, daytype: str, rides: int) -> None:
        self.route = route
        self.date = date
        self.daytype = daytype
        self.rides = rides


def _iter_bus_csv_rows(csv_filename: Path) -> Iterator[list[str]]:
    with csv_filename.open(encoding="utf-8", newline="") as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)
        yield from csv_reader


def _parse_bus_row_fields(row_fields: list[str]) -> tuple[str, str, str, int]:
    if len(row_fields) < 4:
        raise ValueError(f"Fila CSV incompleta: {row_fields!r}")
    route_name, ride_date, day_type, rides_text = row_fields[0], row_fields[1], row_fields[2], row_fields[3]
    try:
        passenger_count = int(rides_text)
    except ValueError as exc:
        raise ValueError(f"Valor de pasajeros inválido: {rides_text!r}") from exc
    return route_name, ride_date, day_type, passenger_count


def read_rides_as_tuples(csv_filename: str | Path) -> list[BusRideTuple]:
    records: list[BusRideTuple] = []
    for row_fields in _iter_bus_csv_rows(Path(csv_filename)):
        route_name, ride_date, day_type, passenger_count = _parse_bus_row_fields(row_fields)
        records.append((route_name, ride_date, day_type, passenger_count))
    return records


def read_rides_as_dicts(csv_filename: str | Path) -> RideData:
    """Lee viajes en RideData (almacenamiento columnar, interfaz de dicts) — ej. 2.5."""
    ride_collection = RideData()
    for row_fields in _iter_bus_csv_rows(Path(csv_filename)):
        route_name, ride_date, day_type, passenger_count = _parse_bus_row_fields(row_fields)
        ride_collection.append(
            {
                "route": route_name,
                "date": ride_date,
                "daytype": day_type,
                "rides": passenger_count,
            }
        )
    return ride_collection


def read_rides_as_namedtuples(csv_filename: str | Path) -> list[BusRideNamedTuple]:
    records: list[BusRideNamedTuple] = []
    for row_fields in _iter_bus_csv_rows(Path(csv_filename)):
        route_name, ride_date, day_type, passenger_count = _parse_bus_row_fields(row_fields)
        records.append(BusRideNamedTuple(route_name, ride_date, day_type, passenger_count))
    return records


def read_rides_as_instances(csv_filename: str | Path) -> list[BusRideRow]:
    records: list[BusRideRow] = []
    for row_fields in _iter_bus_csv_rows(Path(csv_filename)):
        route_name, ride_date, day_type, passenger_count = _parse_bus_row_fields(row_fields)
        records.append(BusRideRow(route_name, ride_date, day_type, passenger_count))
    return records


def read_rides_as_slots_instances(csv_filename: str | Path) -> list[BusRideSlotsRow]:
    records: list[BusRideSlotsRow] = []
    for row_fields in _iter_bus_csv_rows(Path(csv_filename)):
        route_name, ride_date, day_type, passenger_count = _parse_bus_row_fields(row_fields)
        records.append(BusRideSlotsRow(route_name, ride_date, day_type, passenger_count))
    return records


def read_rides_as_plain_dict_list(csv_filename: str | Path) -> list[BusRideRecord]:
    """Lista real de dicts (alto uso de memoria) para comparaciones en 2.1."""
    records: list[BusRideRecord] = []
    for row_fields in _iter_bus_csv_rows(Path(csv_filename)):
        route_name, ride_date, day_type, passenger_count = _parse_bus_row_fields(row_fields)
        records.append(
            {
                "route": route_name,
                "date": ride_date,
                "daytype": day_type,
                "rides": passenger_count,
            }
        )
    return records


def read_rides_as_columns(csv_filename: str | Path) -> dict[str, list[Any]]:
    routes: list[str] = []
    dates: list[str] = []
    daytypes: list[str] = []
    passenger_counts: list[int] = []
    for row_fields in _iter_bus_csv_rows(Path(csv_filename)):
        route_name, ride_date, day_type, count = _parse_bus_row_fields(row_fields)
        routes.append(route_name)
        dates.append(ride_date)
        daytypes.append(day_type)
        passenger_counts.append(count)
    return {
        "routes": routes,
        "dates": dates,
        "daytypes": daytypes,
        "numrides": passenger_counts,
    }


def measure_memory_peak(load_function: Callable[[], Any]) -> tuple[Any, int, int]:
    """Mide memoria actual y pico tras ejecutar una función de carga."""
    tracemalloc.start()
    loaded_data = load_function()
    current_bytes, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return loaded_data, current_bytes, peak_bytes


# ===================================================================
# Ejercicio 2.2 — readport.py, collections y análisis CTA
# ===================================================================


def read_portfolio(csv_filename: str | Path) -> list[PortfolioRecord]:
    portfolio: list[PortfolioRecord] = []
    with Path(csv_filename).open(encoding="utf-8", newline="") as csv_file:
        csv_reader = csv.reader(csv_file)
        headers = next(csv_reader)
        if len(headers) < 3:
            raise ValueError(f"Encabezados insuficientes en {csv_filename}")
        for row_fields in csv_reader:
            if len(row_fields) < 3:
                raise ValueError(f"Fila de portafolio incompleta: {row_fields!r}")
            try:
                share_count = int(row_fields[1])
                unit_price = float(row_fields[2])
            except ValueError as exc:
                raise ValueError(f"Conversión numérica fallida en {row_fields!r}") from exc
            portfolio.append(
                {
                    "name": row_fields[0],
                    "shares": share_count,
                    "price": unit_price,
                }
            )
    return portfolio


def filter_holdings_over_shares(
    portfolio: Sequence[PortfolioRecord], minimum_shares: int
) -> list[PortfolioRecord]:
    return [position for position in portfolio if position["shares"] > minimum_shares]


def portfolio_total_cost(portfolio: Sequence[PortfolioRecord]) -> float:
    return sum(position["shares"] * position["price"] for position in portfolio)


def unique_stock_names(portfolio: Sequence[PortfolioRecord]) -> set[str]:
    return {position["name"] for position in portfolio}


def total_shares_by_name(portfolio: Sequence[PortfolioRecord]) -> dict[str, int]:
    share_totals = {position["name"]: 0 for position in portfolio}
    for position in portfolio:
        share_totals[position["name"]] += position["shares"]
    return share_totals


def total_shares_counter(portfolio: Sequence[PortfolioRecord]) -> Counter[str]:
    share_counter: Counter[str] = Counter()
    for position in portfolio:
        share_counter[position["name"]] += position["shares"]
    return share_counter


def group_portfolio_by_name(
    portfolio: Sequence[PortfolioRecord],
) -> defaultdict[str, list[PortfolioRecord]]:
    positions_by_name: defaultdict[str, list[PortfolioRecord]] = defaultdict(list)
    for position in portfolio:
        positions_by_name[position["name"]].append(position)
    return positions_by_name


def _extract_year_from_date(date_text: str) -> int:
    parts = date_text.split("/")
    if len(parts) != 3:
        raise ValueError(f"Formato de fecha inválido: {date_text!r}")
    return int(parts[2])


class CtaBusAnalyzer:
    """Análisis de datos de la CTA sobre una secuencia de registros de viaje."""

    def __init__(self, ride_records: Sequence[BusRideRecord]) -> None:
        self._ride_records = ride_records

    def count_unique_routes(self) -> int:
        return len({record["route"] for record in self._ride_records})

    def passengers_on_route_and_date(self, route: str, date: str) -> int:
        for record in self._ride_records:
            if record["route"] == route and record["date"] == date:
                return int(record["rides"])
        raise LookupError(f"No hay datos para ruta {route!r} en fecha {date!r}")

    def total_passengers_by_route(self) -> Counter[str]:
        route_totals: Counter[str] = Counter()
        for record in self._ride_records:
            route_totals[record["route"]] += int(record["rides"])
        return route_totals

    def top_routes_by_decade_growth(
        self,
        start_year: int = 2001,
        end_year: int = 2011,
        top_count: int = 5,
    ) -> list[tuple[str, int]]:
        yearly_totals: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))
        for record in self._ride_records:
            ride_year = _extract_year_from_date(record["date"])
            if start_year <= ride_year <= end_year:
                yearly_totals[record["route"]][ride_year] += int(record["rides"])

        decade_growth = {
            route: year_map.get(end_year, 0) - year_map.get(start_year, 0)
            for route, year_map in yearly_totals.items()
        }
        ranked_routes = sorted(decade_growth.items(), key=lambda item: item[1], reverse=True)
        return ranked_routes[:top_count]


# ===================================================================
# Ejercicio 2.3 — Iteración, zip, enumerate y generadores
# ===================================================================


def group_csv_rows_by_name(rows: Sequence[list[str]]) -> dict[str, list[list[str]]]:
    grouped_rows: defaultdict[str, list[list[str]]] = defaultdict(list)
    for stock_name, *remaining_fields in rows:
        grouped_rows[stock_name].append(remaining_fields)
    return dict(grouped_rows)


def rows_with_index(rows: Sequence[list[str]]) -> list[tuple[int, list[str]]]:
    return [(row_number, row) for row_number, row in enumerate(rows)]


def row_to_record(headers: Sequence[str], row_fields: Sequence[str]) -> dict[str, str]:
    if len(headers) != len(row_fields):
        raise ValueError("Encabezados y fila deben tener la misma longitud")
    return dict(zip(headers, row_fields))


def iter_portfolio_records(csv_filename: str | Path) -> Iterator[PortfolioRecord]:
    with Path(csv_filename).open(encoding="utf-8", newline="") as csv_file:
        csv_reader = csv.reader(csv_file)
        headers = next(csv_reader)
        column_types: list[ColumnConverter] = [str, int, float]
        for row_fields in csv_reader:
            yield {
                header: converter(value)
                for header, converter, value in zip(headers, column_types, row_fields)
            }


def iter_bus_ride_dicts(csv_filename: str | Path) -> Iterator[BusRideRecord]:
    with Path(csv_filename).open(encoding="utf-8", newline="") as csv_file:
        csv_reader = csv.reader(csv_file)
        headers = next(csv_reader)
        for row_fields in csv_reader:
            yield dict(zip(headers, row_fields))


def filtered_route_records(
    ride_records: Iterator[BusRideRecord], route: str
) -> Iterator[BusRideRecord]:
    return (record for record in ride_records if record["route"] == route)


def max_passengers_record(ride_records: Iterator[BusRideRecord]) -> BusRideRecord:
    return max(ride_records, key=lambda record: int(record["rides"]))


def square_numbers(numbers: Sequence[int]) -> Iterator[int]:
    for number in numbers:
        yield number * number


def portfolio_reductions(portfolio: Sequence[PortfolioRecord]) -> dict[str, Any]:
    return {
        "total_cost": sum(position["shares"] * position["price"] for position in portfolio),
        "min_shares": min(position["shares"] for position in portfolio),
        "has_ibm": any(position["name"] == "IBM" for position in portfolio),
        "all_ibm": all(position["name"] == "IBM" for position in portfolio),
        "ibm_shares": sum(
            position["shares"] for position in portfolio if position["name"] == "IBM"
        ),
    }


def join_as_strings(values: Sequence[Any]) -> str:
    return ",".join(str(value) for value in values)


# ===================================================================
# Ejercicio 2.4 — mutint.py: entero mutable
# ===================================================================


@total_ordering
class MutInt:
    """Entero mutable con operadores aritméticos y comparación."""

    __slots__ = ("value",)

    def __init__(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError(f"MutInt requiere un int, recibió {type(value).__name__}")
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"MutInt({self.value!r})"

    def __format__(self, format_spec: str) -> str:
        return format(self.value, format_spec)

    def __add__(self, other: object) -> MutInt:
        if isinstance(other, MutInt):
            return MutInt(self.value + other.value)
        if isinstance(other, int):
            return MutInt(self.value + other)
        return NotImplemented

    __radd__ = __add__

    def __iadd__(self, other: object) -> MutInt:
        if isinstance(other, MutInt):
            self.value += other.value
            return self
        if isinstance(other, int):
            self.value += other
            return self
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        if isinstance(other, MutInt):
            return self.value == other.value
        if isinstance(other, int):
            return self.value == other
        return NotImplemented

    def __lt__(self, other: object) -> bool:
        if isinstance(other, MutInt):
            return self.value < other.value
        if isinstance(other, int):
            return self.value < other
        return NotImplemented

    def __int__(self) -> int:
        return self.value

    def __float__(self) -> float:
        return float(self.value)

    __index__ = __int__


# ===================================================================
# Ejercicio 2.5 — RideData: contenedor columnar que finge secuencia de dicts
# ===================================================================


class RideData(collections.abc.Sequence):
    """
    Almacena viajes en columnas pero expone registros como diccionarios.
    Patrón Facade sobre almacenamiento columnar.
    """

    def __init__(
        self,
        routes: Sequence[str] | None = None,
        dates: Sequence[str] | None = None,
        daytypes: Sequence[str] | None = None,
        passenger_counts: Sequence[int] | None = None,
    ) -> None:
        self.routes = list(routes) if routes is not None else []
        self.dates = list(dates) if dates is not None else []
        self.daytypes = list(daytypes) if daytypes is not None else []
        self.numrides = list(passenger_counts) if passenger_counts is not None else []
        self._validate_column_lengths()

    def _validate_column_lengths(self) -> None:
        column_lengths = {
            len(self.routes),
            len(self.dates),
            len(self.daytypes),
            len(self.numrides),
        }
        if len(column_lengths) > 1:
            raise ValueError(f"Longitudes de columna inconsistentes: {column_lengths}")

    def __len__(self) -> int:
        return len(self.routes)

    def append(self, ride_record: Mapping[str, Any]) -> None:
        required_keys = ("route", "date", "daytype", "rides")
        missing_keys = [key for key in required_keys if key not in ride_record]
        if missing_keys:
            raise KeyError(f"Registro incompleto, faltan claves: {missing_keys}")
        self.routes.append(str(ride_record["route"]))
        self.dates.append(str(ride_record["date"]))
        self.daytypes.append(str(ride_record["daytype"]))
        self.numrides.append(int(ride_record["rides"]))

    def _record_at_index(self, index: int) -> BusRideRecord:
        return {
            "route": self.routes[index],
            "date": self.dates[index],
            "daytype": self.daytypes[index],
            "rides": self.numrides[index],
        }

    def __getitem__(self, index: int | slice) -> BusRideRecord | RideData:
        if isinstance(index, slice):
            return RideData(
                routes=self.routes[index],
                dates=self.dates[index],
                daytypes=self.daytypes[index],
                passenger_counts=self.numrides[index],
            )
        return self._record_at_index(index)


# ===================================================================
# Ejercicio 2.6 — reader.py: funciones de primera clase e interning
# ===================================================================


class DataCollection(collections.abc.Sequence):
    """Contenedor columnar genérico con interfaz de secuencia de diccionarios."""

    def __init__(self, headers: Sequence[str], columns: Mapping[str, list[Any]]) -> None:
        self._headers = list(headers)
        self._columns = {header: list(columns[header]) for header in self._headers}
        column_lengths = {len(self._columns[header]) for header in self._headers}
        if len(column_lengths) > 1:
            raise ValueError(f"Columnas con longitudes distintas: {column_lengths}")

    def __len__(self) -> int:
        if not self._headers:
            return 0
        return len(self._columns[self._headers[0]])

    def _record_at_index(self, index: int) -> dict[str, Any]:
        return {header: self._columns[header][index] for header in self._headers}

    def __getitem__(self, index: int | slice) -> dict[str, Any] | DataCollection:
        if isinstance(index, slice):
            sliced_columns = {
                header: self._columns[header][index] for header in self._headers
            }
            return DataCollection(self._headers, sliced_columns)
        return self._record_at_index(index)


def read_csv_as_dicts(
    csv_filename: str | Path,
    column_types: Sequence[ColumnConverter],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with Path(csv_filename).open(encoding="utf-8", newline="") as csv_file:
        csv_reader = csv.reader(csv_file)
        headers = next(csv_reader)
        if len(column_types) != len(headers):
            raise ValueError(
                f"Se esperaban {len(headers)} tipos, se recibieron {len(column_types)}"
            )
        for row_fields in csv_reader:
            if len(row_fields) != len(headers):
                raise ValueError(f"Fila con longitud incorrecta: {row_fields!r}")
            try:
                record = {
                    header: converter(value)
                    for header, converter, value in zip(headers, column_types, row_fields)
                }
            except (ValueError, TypeError) as exc:
                raise ValueError(f"Error convirtiendo fila {row_fields!r}") from exc
            records.append(record)
    return records


def read_csv_as_columns(
    csv_filename: str | Path,
    column_types: Sequence[ColumnConverter],
) -> DataCollection:
    with Path(csv_filename).open(encoding="utf-8", newline="") as csv_file:
        csv_reader = csv.reader(csv_file)
        headers = next(csv_reader)
        if len(column_types) != len(headers):
            raise ValueError(
                f"Se esperaban {len(headers)} tipos, se recibieron {len(column_types)}"
            )
        columns: dict[str, list[Any]] = {header: [] for header in headers}
        for row_fields in csv_reader:
            if len(row_fields) != len(headers):
                raise ValueError(f"Fila con longitud incorrecta: {row_fields!r}")
            for header, converter, raw_value in zip(headers, column_types, row_fields):
                try:
                    columns[header].append(converter(raw_value))
                except (ValueError, TypeError) as exc:
                    raise ValueError(
                        f"Error convirtiendo columna {header!r} valor {raw_value!r}"
                    ) from exc
        return DataCollection(headers, columns)


def count_unique_string_object_ids(
    records: Sequence[Mapping[str, Any]], field_name: str
) -> int:
    return len({id(record[field_name]) for record in records})


def demonstrate_list_growth_sizes() -> list[int]:
    """Observa cómo crece sys.getsizeof de una lista con append (2.5a)."""
    growing_list: list[int] = []
    size_snapshots = [sys.getsizeof(growing_list)]
    for value in range(1, 6):
        growing_list.append(value)
        size_snapshots.append(sys.getsizeof(growing_list))
    return size_snapshots


def demonstrate_dict_growth_sizes() -> list[int]:
    """Observa saltos de memoria al crecer un diccionario (2.5b)."""
    row_dict: dict[str, Any] = {
        "route": "22",
        "date": "01/01/2001",
        "daytype": "U",
        "rides": 7354,
    }
    sizes = [sys.getsizeof(row_dict)]
    row_dict["a"] = 1
    sizes.append(sys.getsizeof(row_dict))
    row_dict["b"] = 2
    sizes.append(sys.getsizeof(row_dict))
    del row_dict["b"]
    sizes.append(sys.getsizeof(row_dict))
    return sizes


# ===================================================================
# Pruebas unitarias
# ===================================================================


class TestReadRides(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ctabus_available = CTABUS_CSV.exists()

    def test_read_tuples_first_record(self) -> None:
        if not self.ctabus_available:
            self.skipTest("ctabus.csv no disponible")
        records = read_rides_as_tuples(CTABUS_CSV)
        self.assertEqual(len(records), 577563)
        self.assertEqual(records[0], ("3", "01/01/2001", "U", 7354))

    def test_ride_data_matches_dict_interface(self) -> None:
        if not self.ctabus_available:
            self.skipTest("ctabus.csv no disponible")
        ride_data = read_rides_as_dicts(CTABUS_CSV)
        self.assertEqual(len(ride_data), 577563)
        self.assertEqual(
            ride_data[0],
            {"route": "3", "date": "01/01/2001", "daytype": "U", "rides": 7354},
        )

    def test_column_storage_length(self) -> None:
        if not self.ctabus_available:
            self.skipTest("ctabus.csv no disponible")
        columns = read_rides_as_columns(CTABUS_CSV)
        self.assertEqual(len(columns["routes"]), 577563)
        self.assertEqual(columns["numrides"][1], 9288)


class TestReadPortfolio(unittest.TestCase):
    def setUp(self) -> None:
        if not PORTFOLIO_CSV.exists():
            self.skipTest("portfolio.csv no disponible")
        self.portfolio = read_portfolio(PORTFOLIO_CSV)

    def test_portfolio_structure(self) -> None:
        self.assertEqual(len(self.portfolio), 7)
        self.assertEqual(self.portfolio[0]["name"], "AA")

    def test_comprehensions_and_counter(self) -> None:
        large_holdings = filter_holdings_over_shares(self.portfolio, 100)
        holding_names = {position["name"] for position in large_holdings}
        self.assertEqual(holding_names, {"CAT", "MSFT"})
        self.assertAlmostEqual(portfolio_total_cost(self.portfolio), 44671.15)
        self.assertEqual(unique_stock_names(self.portfolio), {"MSFT", "IBM", "AA", "GE", "CAT"})
        self.assertEqual(
            dict(total_shares_counter(self.portfolio)),
            {"MSFT": 250, "IBM": 150, "CAT": 150, "AA": 100, "GE": 95},
        )

    def test_defaultdict_grouping(self) -> None:
        by_name = group_portfolio_by_name(self.portfolio)
        self.assertEqual(len(by_name["IBM"]), 2)
        self.assertEqual(by_name["AA"][0]["shares"], 100)


class TestCtaAnalysis(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not CTABUS_CSV.exists():
            cls.analyzer = None
            return
        cls.analyzer = CtaBusAnalyzer(read_rides_as_dicts(CTABUS_CSV))

    def setUp(self) -> None:
        if self.analyzer is None:
            self.skipTest("ctabus.csv no disponible")

    def test_unique_routes(self) -> None:
        self.assertEqual(self.analyzer.count_unique_routes(), 181)

    def test_passengers_route_22_date(self) -> None:
        self.assertEqual(
            self.analyzer.passengers_on_route_and_date("22", "02/02/2011"), 5055
        )

    def test_total_passengers_top_routes(self) -> None:
        totals = self.analyzer.total_passengers_by_route()
        self.assertEqual(
            totals.most_common(3),
            [("79", 133796763), ("9", 117923787), ("49", 95915008)],
        )

    def test_decade_growth_top_five(self) -> None:
        top_growth = self.analyzer.top_routes_by_decade_growth()
        self.assertEqual(
            top_growth,
            [
                ("15", 2732209),
                ("147", 2107910),
                ("66", 1612958),
                ("12", 1612067),
                ("14", 1351308),
            ],
        )


class TestIteration(unittest.TestCase):
    def setUp(self) -> None:
        if not PORTFOLIO_CSV.exists():
            self.skipTest("portfolio.csv no disponible")
        with PORTFOLIO_CSV.open(encoding="utf-8", newline="") as csv_file:
            csv_reader = csv.reader(csv_file)
            self.headers = next(csv_reader)
            self.rows = list(csv_reader)

    def test_unpacking_and_grouping(self) -> None:
        grouped = group_csv_rows_by_name(self.rows)
        self.assertEqual(grouped["IBM"], [["50", "91.10"], ["100", "70.44"]])

    def test_enumerate_rows(self) -> None:
        indexed = rows_with_index(self.rows)
        self.assertEqual(indexed[0], (0, ["AA", "100", "32.20"]))

    def test_zip_to_dict(self) -> None:
        record = row_to_record(self.headers, self.rows[0])
        self.assertEqual(record, {"name": "AA", "shares": "100", "price": "32.20"})

    def test_generator_expressions(self) -> None:
        portfolio = read_portfolio(PORTFOLIO_CSV)
        reductions = portfolio_reductions(portfolio)
        self.assertAlmostEqual(reductions["total_cost"], 44671.15)
        self.assertEqual(reductions["min_shares"], 50)
        self.assertTrue(reductions["has_ibm"])
        self.assertFalse(reductions["all_ibm"])
        self.assertEqual(reductions["ibm_shares"], 150)

    def test_square_generator(self) -> None:
        self.assertEqual(list(square_numbers([1, 2, 3])), [1, 4, 9])

    def test_join_with_str_conversion(self) -> None:
        self.assertEqual(join_as_strings(("GOOG", 100, 490.10)), "GOOG,100,490.1")

    def test_generator_max_route_22(self) -> None:
        if not CTABUS_CSV.exists():
            self.skipTest("ctabus.csv no disponible")
        ride_stream = iter_bus_ride_dicts(CTABUS_CSV)
        route_22_stream = filtered_route_records(ride_stream, "22")
        peak_record = max_passengers_record(route_22_stream)
        self.assertEqual(peak_record["date"], "06/11/2008")
        self.assertEqual(int(peak_record["rides"]), 26896)


class TestMutInt(unittest.TestCase):
    def test_repr_str_format(self) -> None:
        mutable_int = MutInt(3)
        self.assertEqual(str(mutable_int), "3")
        self.assertEqual(repr(mutable_int), "MutInt(3)")
        self.assertEqual(f"The value is {mutable_int:*^10d}", "The value is ****3*****")

    def test_add_and_radd(self) -> None:
        mutable_int = MutInt(3)
        self.assertEqual((mutable_int + 10).value, 13)
        self.assertEqual((10 + mutable_int).value, 13)

    def test_iadd_mutability(self) -> None:
        mutable_int = MutInt(3)
        alias = mutable_int
        mutable_int += 10
        self.assertEqual(mutable_int.value, 13)
        self.assertIs(alias, mutable_int)
        self.assertEqual(alias.value, 13)

    def test_float_addition_not_supported(self) -> None:
        with self.assertRaises(TypeError):
            _ = MutInt(3) + 3.5

    def test_comparisons(self) -> None:
        first = MutInt(3)
        second = MutInt(3)
        third = MutInt(4)
        self.assertTrue(first == second)
        self.assertTrue(first == 3)
        self.assertTrue(first < third)
        self.assertTrue(first <= third)

    def test_conversions_and_indexing(self) -> None:
        mutable_int = MutInt(1)
        self.assertEqual(int(mutable_int), 1)
        self.assertEqual(float(mutable_int), 1.0)
        names = ["Dave", "Guido", "Paula", "Thomas", "Lewis"]
        self.assertEqual(names[mutable_int], "Guido")

    def test_invalid_constructor_type(self) -> None:
        with self.assertRaises(TypeError):
            MutInt(3.5)  # type: ignore[arg-type]


class TestRideData(unittest.TestCase):
    def test_append_and_getitem(self) -> None:
        ride_data = RideData()
        ride_data.append(
            {"route": "3", "date": "01/01/2001", "daytype": "U", "rides": 7354}
        )
        self.assertEqual(len(ride_data), 1)
        self.assertEqual(ride_data[0]["rides"], 7354)

    def test_slice_returns_ride_data(self) -> None:
        ride_data = RideData(
            routes=["3", "4", "6"],
            dates=["01/01/2001"] * 3,
            daytypes=["U"] * 3,
            passenger_counts=[7354, 9288, 6048],
        )
        slice_view = ride_data[0:2]
        self.assertIsInstance(slice_view, RideData)
        self.assertEqual(len(slice_view), 2)
        self.assertEqual(slice_view[1]["route"], "4")

    def test_append_missing_key_raises(self) -> None:
        ride_data = RideData()
        with self.assertRaises(KeyError):
            ride_data.append({"route": "3"})


class TestReader(unittest.TestCase):
    def test_read_csv_as_dicts_portfolio(self) -> None:
        if not PORTFOLIO_CSV.exists():
            self.skipTest("portfolio.csv no disponible")
        portfolio = read_csv_as_dicts(PORTFOLIO_CSV, [str, int, float])
        self.assertEqual(portfolio[0], {"name": "AA", "shares": 100, "price": 32.2})
        self.assertAlmostEqual(
            sum(position["shares"] * position["price"] for position in portfolio),
            44671.15,
        )

    def test_read_csv_as_columns_ctabus(self) -> None:
        if not CTABUS_CSV.exists():
            self.skipTest("ctabus.csv no disponible")
        column_data = read_csv_as_columns(CTABUS_CSV, [str, str, str, int])
        self.assertEqual(len(column_data), 577563)
        self.assertEqual(
            column_data[0],
            {"route": "3", "date": "01/01/2001", "daytype": "U", "rides": 7354},
        )
        sliced = column_data[0:3]
        self.assertIsInstance(sliced, DataCollection)
        self.assertEqual(len(sliced), 3)

    def test_intern_reduces_route_string_ids(self) -> None:
        if not CTABUS_CSV.exists():
            self.skipTest("ctabus.csv no disponible")
        plain_rows = read_csv_as_dicts(CTABUS_CSV, [str, str, str, int])
        interned_rows = read_csv_as_dicts(CTABUS_CSV, [sys.intern, str, str, int])
        self.assertGreater(count_unique_string_object_ids(plain_rows, "route"), 181)
        self.assertEqual(count_unique_string_object_ids(interned_rows, "route"), 181)

    def test_column_reader_works_with_cta_analyzer(self) -> None:
        if not CTABUS_CSV.exists():
            self.skipTest("ctabus.csv no disponible")
        column_data = read_csv_as_columns(
            CTABUS_CSV, [sys.intern, sys.intern, str, int]
        )
        analyzer = CtaBusAnalyzer(column_data)
        self.assertEqual(analyzer.count_unique_routes(), 181)

    def test_mismatched_types_raises(self) -> None:
        if not PORTFOLIO_CSV.exists():
            self.skipTest("portfolio.csv no disponible")
        with self.assertRaises(ValueError):
            read_csv_as_dicts(PORTFOLIO_CSV, [str, int])


class TestMemoryDemos(unittest.TestCase):
    def test_list_size_grows_on_capacity_jump(self) -> None:
        sizes = demonstrate_list_growth_sizes()
        self.assertGreater(sizes[1], sizes[0])
        self.assertGreaterEqual(sizes[5], sizes[4])
        self.assertGreater(sizes[-1], sizes[0])

    def test_dict_size_jumps_after_fifth_key(self) -> None:
        sizes = demonstrate_dict_growth_sizes()
        self.assertEqual(sizes[0], sizes[1])
        self.assertGreater(sizes[2], sizes[1])


def _demo_exercises() -> None:
    if PORTFOLIO_CSV.exists():
        portfolio = read_portfolio(PORTFOLIO_CSV)
        assert portfolio_total_cost(portfolio) == 44671.15

    mutable_int = MutInt(3)
    assert mutable_int + 10 == MutInt(13)

    ride_data = RideData()
    ride_data.append(
        {"route": "22", "date": "06/11/2008", "daytype": "W", "rides": 26896}
    )
    assert ride_data[0]["rides"] == 26896

    print("Todas las demostraciones del capítulo 2 pasaron correctamente.")


if __name__ == "__main__":
    unittest.main()
