"""
Clase base Structure para estructuras de datos declarativas (ejercicios 6.1-6.4).
"""

from __future__ import annotations

import inspect
import sys
from typing import Any, Tuple


class Structure:
    """
    Clase base para estructuras de datos declarativas.

    Las subclases definen ``_fields`` y llaman a ``create_init()`` para
    generar automáticamente un constructor con firma explícita (vía exec).
    """

    _fields: Tuple[str, ...] = ()

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
    def create_init(cls) -> None:
        """Genera dinámicamente ``__init__`` a partir de ``_fields`` (ej. 6.4)."""
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

    # --- Enfoques intermedios del capítulo 6 (referencia educativa) ---

    @staticmethod
    def _init() -> None:
        """
        Inicializa atributos inspeccionando el frame del llamador (ej. 6.2).
        Conservado como referencia; reemplazado por create_init() en 6.4.
        """
        caller_locals = sys._getframe(1).f_locals
        instance = caller_locals["self"]
        for local_name, local_value in caller_locals.items():
            if local_name == "self":
                continue
            setattr(instance, local_name, local_value)

    @classmethod
    def set_fields(cls) -> None:
        """
        Deriva ``_fields`` de la firma de ``__init__`` (ej. 6.3).
        Conservado como referencia; reemplazado por _fields explícito en 6.4.
        """
        init_signature = inspect.signature(cls.__init__)
        cls._fields = tuple(
            name for name in init_signature.parameters if name != "self"
        )


class Date(Structure):
    """Estructura de ejemplo del ejercicio 6.1."""

    _fields = ("year", "month", "day")


Date.create_init()
