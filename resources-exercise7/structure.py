"""
Clase base Structure con metaclase y decorador de atributos (ejercicios 6.x y 7.x).
"""

from __future__ import annotations

from collections import ChainMap
from typing import Any, Sequence, Tuple

from validate import Integer, Validator, validated


class StructureMeta(type):
    """
    Metaclase que inyecta validators en el namespace de definición de clase (ej. 7.6).
    Patrón: Metaclass.
    """

    @classmethod
    def __prepare__(metacls, class_name: str, bases: tuple[type, ...]) -> ChainMap:
        return ChainMap({}, Validator.validators)

    def __new__(
        metacls,
        class_name: str,
        bases: tuple[type, ...],
        namespace: ChainMap | dict[str, Any],
    ) -> StructureMeta:
        if hasattr(namespace, "maps"):
            class_attributes = namespace.maps[0]
        else:
            class_attributes = namespace
        return super().__new__(metacls, class_name, bases, class_attributes)


class Structure(metaclass=StructureMeta):
    """Clase base para estructuras de datos con campos validados."""

    _fields: Tuple[str, ...] = ()
    _types: Tuple[Any, ...] = ()

    def __setattr__(self, attribute_name: str, attribute_value: Any) -> None:
        is_private_attribute = attribute_name.startswith("_")
        is_declared_field = attribute_name in self._fields

        if is_private_attribute or is_declared_field:
            super().__setattr__(attribute_name, attribute_value)
        else:
            raise AttributeError(f"No attribute {attribute_name}")

    def __repr__(self) -> str:
        formatted_fields = ", ".join(
            repr(getattr(self, field_name)) for field_name in self._fields
        )
        return f"{type(self).__name__}({formatted_fields})"

    @classmethod
    def from_row(cls, row: Sequence[str]) -> Structure:
        """Crea una instancia a partir de una fila CSV (ejercicio 7.3d)."""
        converted_values = [
            type_converter(raw_value)
            for type_converter, raw_value in zip(cls._types, row)
        ]
        return cls(*converted_values)

    @classmethod
    def create_init(cls) -> None:
        """Genera dinámicamente ``__init__`` a partir de ``_fields``."""
        if not cls._fields:
            raise ValueError(
                f"{cls.__name__} debe definir _fields antes de llamar a create_init()"
            )

        argument_list = ", ".join(cls._fields)
        assignment_lines = [
            f"    self.{field_name} = {field_name}" for field_name in cls._fields
        ]
        init_source_code = (
            f"def __init__(self, {argument_list}):\n" + "\n".join(assignment_lines)
        )

        generated_namespace: dict[str, Any] = {}
        exec(init_source_code, generated_namespace)
        cls.__init__ = generated_namespace["__init__"]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Structure):
            return NotImplemented
        return all(
            getattr(self, field_name) == getattr(other, field_name)
            for field_name in self._fields
        )

    @classmethod
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        validate_attributes(cls)


def validate_attributes(cls: type) -> type:
    """
    Escanea validators y métodos anotados; configura _fields, _types e __init__.
    Patrón: Class Decorator (aplicado vía __init_subclass__).
    """
    field_validators: list[Validator] = []

    for attribute_name, attribute_value in vars(cls).items():
        if isinstance(attribute_value, Validator):
            field_validators.append(attribute_value)

        elif callable(attribute_value) and attribute_value.__annotations__:
            setattr(cls, attribute_name, validated(attribute_value))

    cls._fields = tuple(validator.name for validator in field_validators)
    cls._types = tuple(
        getattr(validator, "expected_type", lambda value: value)
        for validator in field_validators
    )

    if cls._fields:
        cls.create_init()

    return cls


def typed_structure(class_name: str, **field_validators: Validator) -> type:
    """Factory que crea una Structure tipada con ``type()`` (ejercicio 7.4)."""
    return type(class_name, (Structure,), field_validators)


class Date(Structure):
    """Estructura de ejemplo del ejercicio 6.1."""

    year = Integer()
    month = Integer()
    day = Integer()
