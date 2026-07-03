"""
Módulo simple para explorar importación y recarga (ejercicio 9.1).
"""

x = 42


def foo() -> None:
    print("x is", x)


class Spam:
    def yow(self) -> None:
        print("Yow!")


print("Loaded simplemod")
