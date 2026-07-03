"""
Planificador simple de tareas con generadores (ejercicio 8.5a).
"""

from __future__ import annotations

from collections import deque
from typing import Deque, Generator

tasks: Deque[Generator[None, None, None]] = deque()


def run() -> None:
    """Ejecuta generadores cooperativamente hasta que terminen."""
    while tasks:
        current_task = tasks.popleft()
        try:
            current_task.send(None)
            tasks.append(current_task)
        except StopIteration:
            print("Task done")


def countdown(remaining_seconds: int) -> Generator[None, None, None]:
    while remaining_seconds > 0:
        print("T-minus", remaining_seconds)
        yield
        remaining_seconds -= 1


def countup(limit: int) -> Generator[None, None, None]:
    current_value = 0
    while current_value < limit:
        print("Up we go", current_value)
        yield
        current_value += 1


if __name__ == "__main__":
    tasks.append(countdown(10))
    tasks.append(countdown(5))
    tasks.append(countup(20))
    run()
