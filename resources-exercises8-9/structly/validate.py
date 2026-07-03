"""
Validadores de tipo/valor y decoradores de validación.
"""

from __future__ import annotations

from functools import wraps
from inspect import get_annotations, signature
from typing import Any, Callable, Dict, Optional, Type, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

__all__ = [
    "Validator",
    "Typed",
    "Positive",
    "Integer",
    "Float",
    "String",
    "PositiveInteger",
    "PositiveFloat",
    "validated",
    "enforce",
]


class Validator:
    """Validador base reutilizable como descriptor y en anotaciones."""

    name: Optional[str] = None
    validators: Dict[str, Type[Validator]] = {}

    def __set_name__(self, owner: type, attribute_name: str) -> None:
        self.name = attribute_name

    @classmethod
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls.validators[cls.__name__] = cls

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
    expected_type: type = object

    @classmethod
    def check(cls, value: Any) -> Any:
        if not isinstance(value, cls.expected_type):
            raise TypeError(f"Expected {cls.expected_type}")
        return super().check(value)


class Positive(Validator):
    @classmethod
    def check(cls, value: Any) -> Any:
        if value < 0:
            raise ValueError("must be >= 0")
        return super().check(value)


_TYPED_CLASS_TABLE = [
    ("Integer", int),
    ("Float", float),
    ("String", str),
]

globals().update(
    (
        class_name,
        type(class_name, (Typed,), {"expected_type": python_type}),
    )
    for class_name, python_type in _TYPED_CLASS_TABLE
)


class PositiveInteger(Integer, Positive):
    pass


class PositiveFloat(Float, Positive):
    pass


def validated(wrapped_function: F) -> F:
    function_signature = signature(wrapped_function)
    annotation_globals = dict(wrapped_function.__globals__)
    annotation_globals.update(Validator.validators)
    resolved_annotations = get_annotations(
        wrapped_function, eval_str=True, globals=annotation_globals
    )
    parameter_validators = dict(resolved_annotations)
    return_validator = parameter_validators.pop("return", None)

    @wraps(wrapped_function)
    def wrapper(*positional_args: Any, **keyword_args: Any) -> Any:
        bound_arguments = function_signature.bind(*positional_args, **keyword_args)
        bound_arguments.apply_defaults()
        validation_errors: list[str] = []

        for parameter_name, validator in parameter_validators.items():
            if parameter_name not in bound_arguments.arguments:
                continue
            try:
                validator.check(bound_arguments.arguments[parameter_name])
            except Exception as exc:
                validation_errors.append(f"    {parameter_name}: {exc}")

        if validation_errors:
            raise TypeError("Bad Arguments\n" + "\n".join(validation_errors))

        result = wrapped_function(*positional_args, **keyword_args)

        if return_validator is not None:
            try:
                return_validator.check(result)
            except Exception as exc:
                raise TypeError(f"Bad return: {exc}") from None

        return result

    return wrapper  # type: ignore[return-value]


def enforce(**annotation_validators: Validator) -> Callable[[F], F]:
    return_validator = annotation_validators.pop("return_", None)

    def decorator(wrapped_function: F) -> F:
        function_signature = signature(wrapped_function)

        @wraps(wrapped_function)
        def wrapper(*positional_args: Any, **keyword_args: Any) -> Any:
            bound_arguments = function_signature.bind(*positional_args, **keyword_args)
            bound_arguments.apply_defaults()
            validation_errors: list[str] = []

            for parameter_name, validator in annotation_validators.items():
                try:
                    validator.check(bound_arguments.arguments[parameter_name])
                except Exception as exc:
                    validation_errors.append(f"    {parameter_name}: {exc}")

            if validation_errors:
                raise TypeError("Bad Arguments\n" + "\n".join(validation_errors))

            result = wrapped_function(*positional_args, **keyword_args)

            if return_validator is not None:
                try:
                    return_validator.check(result)
                except Exception as exc:
                    raise TypeError(f"Bad return: {exc}") from None

            return result

        return wrapper  # type: ignore[return-value]

    return decorator
