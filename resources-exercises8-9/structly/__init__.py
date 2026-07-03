"""
Paquete structly: estructuras tipadas, lectura CSV y formateo de tablas.
"""

from . import reader, structure, tableformat, validate
from .reader import *
from .structure import *
from .tableformat import *
from .validate import *

__all__ = [
    *structure.__all__,
    *reader.__all__,
    *tableformat.__all__,
    *validate.__all__,
]
