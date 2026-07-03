# Python-exercises

Ejercicios resueltos del curso **Python para Programadores** (`python-course/`), organizados por capítulos. Los datos de prueba viven en `../python-course/Data/`.

**Autora:** Dayana Siles

---

## Archivos principales

| Archivo | Capítulos | Descripción |
|---------|-----------|-------------|
| `Exercises5-dayanasiles.py` | 5.1 – 5.6 | Solución monolítica (todo en un solo archivo) |
| `Exercises6-dayanasiles.py` | 6.1 – 6.5 | Punto de entrada; módulos en `resources-exercise6/` |
| `Exercises7-dayanasiles.py` | 7.1 – 7.6 | Punto de entrada; módulos en `resources-exercise7/` |
| `Exercises8-9-dayanasiles.py` | 8.1 – 9.4 | Punto de entrada; módulos en `resources-exercises8-9/` |

---

## Capítulo 5 — `Exercises5-dayanasiles.py`

**Ejercicios:** funciones flexibles, retorno de valores, funciones de orden superior, closures, manejo de excepciones/logging y `unittest`.

### Contenido resuelto

- **5.1** — `reader.py`: `csv_as_dicts`, `csv_as_instances`, `read_csv_as_*`, parámetro `headers`, type hints.
- **5.2** — `parse_line()`: devuelve tupla o `None`.
- **5.3** — `convert_csv()` como función de orden superior; `csv_as_dicts` e `csv_as_instances` delegan en ella.
- **5.4** — `counter()` (closure), `TypedProperty` con `__set_name__`, clase `Stock` con validación.
- **5.5** — Captura de `ValueError` en CSV con `logging` (WARNING + DEBUG).
- **5.6** — `TestStock` con 12 pruebas unitarias.

### Decisiones técnicas

- **Archivo único:** el capítulo 5 se consolidó en un solo módulo para facilitar la entrega inicial; no se separaron `reader.py`, `stock.py`, etc.
- **Bucle explícito en `convert_csv`:** se abandonó `map()` del ejercicio 5.3 para poder capturar excepciones fila a fila (requisito 5.5).
- **`get_annotations` no fue necesario aún:** la validación de `Stock` usa properties y descriptores, no decoradores con anotaciones diferidas.
- **Ruta de datos centralizada:** `DATA_DIR` apunta a `python-course/Data` con `pathlib`, independiente del directorio de ejecución.

### Ejecución

```bash
python Exercises5-dayanasiles.py -v
```

---

## Capítulo 6 — `Exercises6-dayanasiles.py`

**Ejercicios:** argumentos variables, `Structure`, metaprogramación con `exec`, validación con objetos invocables.

### Módulos (`resources-exercise6/`)

| Módulo | Rol |
|--------|-----|
| `structure.py` | Clase base `Structure` con `create_init()`, `__setattr__`, `__repr__` |
| `stock.py` | `Stock` sobre `Structure` con validación y `from_row` |
| `orig_stock.py` | Respaldo de la implementación pre-6.1 (`__slots__` + properties) |
| `validate.py` | Jerarquía `Validator` y `ValidatedFunction` (descriptor) |
| `teststock.py`, `teststructure.py`, `testvalidate.py` | Pruebas unitarias |

### Decisiones técnicas

- **Evolución por capítulos conservada:** `Structure` mantiene `_init()` y `set_fields()` como referencia educativa de los enfoques 6.2 y 6.3, aunque la versión final usa `create_init()` (6.4).
- **`ValidatedFunction` como descriptor:** implementa `__get__` para que `@validated` funcione en métodos (desafío 6.5c), no solo en funciones libres.
- **Resolución de anotaciones:** `get_annotations(..., eval_str=True)` combinado con `Validator.validators` para soportar `from __future__ import annotations`.
- **Separación en módulos:** a partir del capítulo 6 el código sigue la estructura que pide el curso (`structure.py`, `stock.py`, `validate.py`, `teststock.py`).
- **`orig_stock.py`:** preserva la versión anterior a la reescritura con `Structure`, tal como sugiere el ejercicio 6.1.

### Ejecución

```bash
python Exercises6-dayanasiles.py
```

---

## Capítulo 7 — `Exercises7-dayanasiles.py`

**Ejercicios:** decoradores, decoradores con argumentos, class decorators, metaclases, inyección de namespace.

### Módulos (`resources-exercise7/`)

| Módulo | Rol |
|--------|-----|
| `logcall.py` | `@logged`, `@logformat(fmt)` con `functools.wraps` |
| `validate.py` | `@validated`, `@enforce`, tipos generados dinámicamente, registry `Validator.validators` |
| `structure.py` | `StructureMeta` + `validate_attributes` vía `__init_subclass__` |
| `stock.py` | `Stock` sin imports explícitos de validators (metaclase 7.6) |
| `reader.py` | Lectura CSV reutilizable |
| `mymeta.py` | Metaclase `mytype` de demostración (7.5) |

### Decisiones técnicas

- **`validated` como función decoradora (no clase):** reescritura del ejercicio 7.1 con mensajes de error estructurados (`Bad Arguments` / `Bad return`) y `@wraps` para preservar metadatos (7.2).
- **`enforce(**validators)`:** alternativa declarativa a las anotaciones de tipo; usa `return_` para el valor de retorno.
- **Generación dinámica de tipos (`Integer`, `Float`, `String`):** tabla `_TYPED_CLASS_TABLE` + `type()` en lugar de clases repetitivas (7.4).
- **`StructureMeta.__prepare__` con `ChainMap`:** inyecta `Validator.validators` en el namespace de definición de clase, eliminando imports en `stock.py` (7.6).
- **Orden de decoradores en métodos:** la clase `Spam` documenta que `@classmethod`/`@property` deben ir *encima* de `@logformat` para que el logging funcione (7.2c).
- **Mensajes de `Positive` en minúsculas:** `must be >= 0` para alinear la salida con los ejemplos del curso en validación de `sell()`.

### Ejecución

```bash
python Exercises7-dayanasiles.py
```

---

## Capítulo 8 y 9 — `Exercises8-9-dayanasiles.py`

**Ejercicios:** generadores, pipelines, coroutines, async/await, módulos y paquetes.

### Módulos (`resources-exercises8-9/`)

| Módulo / paquete | Rol |
|------------------|-----|
| `follow.py` | Generador `follow()` con manejo de `GeneratorExit` |
| `ticker.py` | Pipeline generador: `follow` → `csv.reader` → `Ticker` |
| `cofollow.py` | Coroutines: `consumer`, `receive`, `printer` |
| `coticker.py` | Pipeline con coroutines y `yield from receive()` |
| `multitask.py` | Planificador cooperativo de generadores |
| `server.py` | Servidor echo con `select`, `GenSocket`, `async`/`await` |
| `simplemod.py` | Demostración de importación y `reload()` (9.1) |
| `structly/` | Paquete unificado: `validate`, `structure`, `reader`, `tableformat` |
| `stock.py` | `from structly import *` — clase final del curso |

### Estructura del paquete `structly` (9.2 – 9.4)

```
structly/
├── __init__.py          # re-exporta todo con __all__
├── validate.py
├── structure.py         # + __iter__, __eq__ con tuple(self)
├── reader.py
└── tableformat/
    ├── formatter.py     # TableFormatter + create_formatter
    └── formats/
        ├── text.py
        ├── csv.py
        └── html.py
```

### Decisiones técnicas

- **`__iter__` y `__eq__` en `Structure`:** iteración por `_fields` y comparación con `tuple(self)` (8.1); habilita desempaquetado y `list(stock)`.
- **Pipeline generador vs. coroutines:** `ticker.py` encadena con expresiones generadoras; `coticker.py` envía datos con `.send()` y `yield from receive(tipo)` para validación de mensajes (8.6).
- **`follow()` con `GeneratorExit`:** cierre limpio del archivo al destruir o cerrar el generador (8.4).
- **Tests con `unittest.mock`:** los tests de `follow()` no dependen de `stocksim.py` ni de `stocklog.csv` (evita bloqueos por el bucle infinito y `seek` al final del archivo).
- **Paquete `structly`:** consolidación de módulos con `__all__` por submódulo y `from structly import *` en `stock.py` (9.3b).
- **Registro dinámico de formateadores (9.4):** `TableFormatter.__init_subclass__` + `_ensure_format_registered()` con `importlib`; elimina imports circulares y nombres de clase cableados en `create_formatter()`.
- **`str(value)` en `TextTableFormatter`:** conversión explícita para soportar columnas numéricas (`shares`, `price`) sin error de formato.
- **Carpeta `resources-exercises8-9/`:** separa el código de soporte del punto de entrada, manteniendo el mismo patrón que los capítulos 6 y 7.

### Ejecución

```bash
python Exercises8-9-dayanasiles.py
python stock.py
```

> Los ejercicios de ticker en tiempo real (`follow`, `ticker`, `coticker`) requieren `python stocksim.py` en `python-course/Data/` generando `stocklog.csv`.

---

## Patrones de diseño aplicados (resumen)

| Patrón | Dónde |
|--------|-------|
| Template Method | `Structure` define comportamiento común; subclases declaran campos |
| Decorator | `@logged`, `@validated`, `@enforce`, `@consumer` |
| Decorator Factory | `@logformat(fmt)`, `@enforce(**kwargs)` |
| Descriptor | `TypedProperty`, `ValidatedFunction.__get__`, validators en `Stock` |
| Metaclass | `StructureMeta` con `ChainMap` para inyección de namespace |
| Registry | `Validator.validators`, `TableFormatter._formats` |
| Iterator / Generator | `follow()`, pipelines de `ticker.py` |
| Pipeline | Encadenamiento generador y coroutine |
| Package | `structly` con exports unificados y división de `tableformat/` |

---

## Dependencias entre capítulos

```
Cap. 5 (monolito)
  └── reader, Stock, validators, unittest

Cap. 6 (módulos)
  └── Structure + ValidatedFunction

Cap. 7 (decoradores + metaclase)
  └── validated/enforce, StructureMeta, Stock sin imports

Cap. 8-9 (generadores + paquete structly)
  └── follow/pipelines, structly package, stock.py final
```

Cada capítulo posterior extiende o reemplaza decisiones del anterior sin romper las pruebas heredadas de `teststock.py`.
