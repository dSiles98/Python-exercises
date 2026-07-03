"""
Validadores de tipo/valor y decorador ValidatedFunction (ejercicio 6.5).
"""

from __future__ import annotations

import inspect
from inspect import Signature, get_annotations, signature
from typing import Any, Callable, Optional, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


class Validator:
    """Validador base reutilizable en atributos y anotaciones de funciones."""

    name: Optional[str] = None

    def __set_name__(self, owner: type, attribute_name: str) -> None:
        self.name = attribute_name

    @classmethod
    def check(cls, value: Any) -> Any:
        return value

    def __get__(self, instance: Any, owner: type) -> Any:
        if instance is None:
            return self
        return instance.__dict__[self.name]

    def __set__(self, instance: Any, value: Any) -> None:
        instance.__dict__[self.name] = self.check(value)


class Typed(Validator):
    """Valida que el valor sea una instancia del tipo esperado."""

    expected_type: type = object

    @classmethod
    def check(cls, value: Any) -> Any:
        if not isinstance(value, cls.expected_type):
            raise TypeError(f"Expected {cls.expected_type}")
        return super().check(value)


class Integer(Typed):
    expected_type = int


class Float(Typed):
    expected_type = float


class String(Typed):
    expected_type = str


class Positive(Validator):
    """Valida que el valor numérico sea no negativo."""

    @classmethod
    def check(cls, value: Any) -> Any:
        if value < 0:
            raise ValueError("Must be >= 0")
        return super().check(value)


class PositiveInteger(Integer, Positive):
    pass


class PositiveFloat(Float, Positive):
    pass


class ValidatedFunction:
    """
    Decorator que valida argumentos y retorno según anotaciones de tipo.
    Implementa el protocolo descriptor para funcionar como método de clase.
    """

    def __init__(self, wrapped_function: Callable[..., Any]) -> None:
        self._wrapped_function = wrapped_function
        self._signature: Signature = signature(wrapped_function)
        resolved_annotations = get_annotations(
            wrapped_function, eval_str=True, globals=wrapped_function.__globals__
        )
        self._parameter_validators = dict(resolved_annotations)
        self._return_validator = self._parameter_validators.pop("return", None)
        self.__name__ = wrapped_function.__name__
        self.__doc__ = wrapped_function.__doc__

    def _validate_bound_arguments(self, bound_arguments: inspect.BoundArguments) -> None:
        bound_arguments.apply_defaults()
        for parameter_name, validator in self._parameter_validators.items():
            if parameter_name not in bound_arguments.arguments:
                continue
            argument_value = bound_arguments.arguments[parameter_name]
            validator.check(argument_value)

    def __call__(self, *positional_args: Any, **keyword_args: Any) -> Any:
        bound_arguments = self._signature.bind(*positional_args, **keyword_args)
        self._validate_bound_arguments(bound_arguments)

        result = self._wrapped_function(*positional_args, **keyword_args)

        if self._return_validator is not None:
            self._return_validator.check(result)

        return result

    def __get__(
        self, instance: Any, owner: type
    ) -> ValidatedFunction | Callable[..., Any]:
        """Permite usar el decorador como método enlazado (desafío 6.5c)."""
        if instance is None:
            return self

        def bound_method(*args: Any, **kwargs: Any) -> Any:
            return self(instance, *args, **kwargs)

        bound_method.__name__ = self.__name__
        return bound_method


def validated(function: F) -> F:
    """Atajo decorador para envolver funciones con ValidatedFunction."""
    return ValidatedFunction(function)  # type: ignore[return-value]
