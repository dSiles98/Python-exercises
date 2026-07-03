"""
Decoradores de logging para funciones (ejercicios 7.1 y 7.2).
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def logformat(message_format: str) -> Callable[[F], F]:
    """
    Decorador con argumentos que registra llamadas con un formato personalizado.
    Patrón: Decorator Factory.
    """

    def decorator(wrapped_function: F) -> F:
        print("Adding logging to", wrapped_function.__name__)

        @wraps(wrapped_function)
        def wrapper(*positional_args: Any, **keyword_args: Any) -> Any:
            print(message_format.format(func=wrapped_function))
            return wrapped_function(*positional_args, **keyword_args)

        return wrapper  # type: ignore[return-value]

    return decorator


logged = logformat("Calling {func.__name__}")
