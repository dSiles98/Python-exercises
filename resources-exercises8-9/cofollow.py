"""
Coroutines para seguimiento de archivos y pipelines (ejercicios 8.3-8.6).
"""

from __future__ import annotations

import os
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Generator, Type, TypeVar

T = TypeVar("T")
CoroutineFunction = Callable[..., Generator[Any, Any, Any]]


def consumer(coroutine_function: CoroutineFunction) -> CoroutineFunction:
    """Decorador que inicializa una coroutine con send(None)."""

    @wraps(coroutine_function)
    def starter(*args: Any, **kwargs: Any) -> Generator[Any, Any, Any]:
        pipeline_stage = coroutine_function(*args, **kwargs)
        pipeline_stage.send(None)
        return pipeline_stage

    return starter


def receive(expected_type: Type[T]) -> Generator[T, Any, T]:
    """Recibe y valida un mensaje del tipo esperado (ejercicio 8.6)."""
    message = yield
    assert isinstance(message, expected_type), f"Expected type {expected_type}"
    return message


def follow(log_file_path: str | Path, target: Generator[Any, Any, Any]) -> None:
    """Envía líneas nuevas de un archivo a una coroutine destino."""
    with open(log_file_path, "r") as log_file:
        log_file.seek(0, os.SEEK_END)
        while True:
            line = log_file.readline()
            if line != "":
                target.send(line)
            else:
                time.sleep(0.1)


@consumer
def printer() -> Generator[None, Any, None]:
    """Imprime mensajes recibidos y reporta excepciones (ejercicio 8.4)."""
    while True:
        try:
            item = yield
            print(item)
        except Exception as exc:
            print(f"ERROR: {exc!r}")


if __name__ == "__main__":
    data_dir = Path(__file__).resolve().parent.parent / "python-course" / "Data"
    follow(data_dir / "stocklog.csv", printer())
