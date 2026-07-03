"""
Metaclase de demostración (ejercicio 7.5).
"""

from __future__ import annotations

from typing import Any


class mytype(type):
    """Metaclase que imprime información al crear una clase."""

    def __new__(
        metacls,
        class_name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
    ) -> mytype:
        print("Creating class :", class_name)
        print("Base classes   :", bases)
        print("Attributes     :", list(namespace))
        return super().__new__(metacls, class_name, bases, namespace)


class myobject(metaclass=mytype):
    """Clase base con metaclase de diagnóstico."""

    pass
