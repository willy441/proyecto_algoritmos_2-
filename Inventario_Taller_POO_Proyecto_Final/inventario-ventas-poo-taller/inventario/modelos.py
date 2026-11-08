"""Entidades del sistema: repuestos y ventas registradas."""
from dataclasses import dataclass
from datetime import datetime
import re
from .excepciones import CodigoInvalidoError, DatoInvalidoError, StockInsuficienteError

class Producto:
    """Representa un repuesto con datos validados y existencias protegidas."""
    def __init__(self, codigo: str, nombre: str, categoria: str, precio: float, stock: int):
        """Crea un repuesto; lanza un error si hay valores inválidos."""
        self.codigo = codigo
        self.nombre = nombre
        self.categoria = categoria
        self.precio = precio
        self.stock = stock

    @staticmethod
    def validar_codigo(codigo: str) -> bool:
        """Comprueba el formato de tres letras y tres cifras; retorna bool."""
        return bool(re.fullmatch(r"[A-Z]{3}[0-9]{3}", codigo.strip().upper()))

    @classmethod
    def desde_fila_csv(cls, fila: dict) -> 'Producto':
        """Construye un Producto desde un registro CSV; propaga errores de validación."""
        try:
            return cls(fila['codigo'], fila['nombre'], fila['categoria'], float(fila['precio']), int(fila['stock']))
        except (ValueError, TypeError, KeyError) as error:
            raise DatoInvalidoError(f"Fila CSV inválida: {fila}") from error

    @property
    def codigo(self) -> str:
        """Retorna el código único del producto."""
        return self._codigo

    @codigo.setter
    def codigo(self, valor: str) -> None:
        """Establece el código; lanza CodigoInvalidoError si no cumple el formato."""
        if not self.validar_codigo(valor):
            raise CodigoInvalidoError('El código debe tener 3 letras y 3 números (ejemplo: REP011).')
        self._codigo = valor.strip().upper()

    @property
    def nombre(self) -> str:
        """Retorna el nombre del repuesto."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        """Valida y normaliza el nombre; lanza DatoInvalidoError si está vacío."""
        if not isinstance(valor, str) or not valor.strip():
            raise DatoInvalidoError('El nombre no puede estar vacío.')
        self._nombre = ' '.join(valor.split()).title()

    @property
    def categoria(self) -> str:
        """Retorna la categoría del repuesto."""
        return self._categoria

    @categoria.setter
    def categoria(self, valor: str) -> None:
        """Normaliza la categoría y evita valores vacíos."""
        if not isinstance(valor, str) or not valor.strip():
            raise DatoInvalidoError('La categoría no puede estar vacía.')
        self._categoria = ' '.join(valor.split()).capitalize()

    @property
    def precio(self) -> float:
        """Retorna el precio unitario en quetzales."""
        return self._precio

    @precio.setter
    def precio(self, valor: float) -> None:
        """Valida un precio positivo; lanza DatoInvalidoError si no lo es."""
        try:
            numero = float(valor)
        except (ValueError, TypeError) as error:
            raise DatoInvalidoError('El precio debe ser numérico.') from error
        if not 0 < numero < float('inf'):
            raise DatoInvalidoError('El precio debe ser mayor a cero y finito.')
        self._precio = numero

    @property
    def stock(self) -> int:
        """Retorna las unidades disponibles."""
        return self._stock

    @stock.setter
    def stock(self, valor: int) -> None:
        """Valida un entero no negativo; lanza DatoInvalidoError en caso contrario."""
        if isinstance(valor, bool) or not isinstance(valor, int) or valor < 0:
            raise DatoInvalidoError('El stock debe ser un entero igual o mayor a cero.')
        self._stock = valor

    def descontar_stock(self, cantidad: int) -> None:
        """Resta unidades y lanza StockInsuficienteError si excede el stock."""
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise DatoInvalidoError('La cantidad debe ser un entero mayor a cero.')
        if cantidad > self.stock:
            raise StockInsuficienteError(f'Stock insuficiente: quedan {self.stock} unidades.')
        self.stock = self.stock - cantidad

    def necesita_reabastecer(self, minimo: int = 3) -> bool:
        """Indica si el stock es igual o menor que el mínimo configurado."""
        return self.stock <= minimo

    def a_fila_csv(self) -> dict:
        """Retorna los valores persistibles de este repuesto."""
        return {'codigo': self.codigo, 'nombre': self.nombre, 'categoria': self.categoria,
                'precio': f'{self.precio:.2f}', 'stock': self.stock}

    def __str__(self) -> str:
        """Retorna una descripción corta para el usuario."""
        return f'{self.codigo} - {self.nombre} (Q{self.precio:.2f})'

    def __repr__(self) -> str:
        """Retorna una representación útil para depuración."""
        return f'Producto({self.codigo!r}, {self.nombre!r}, {self.categoria!r}, {self.precio!r}, {self.stock!r})'

@dataclass(frozen=True)
class Venta:
    """Registro inmutable de una venta efectuada."""
    fecha_hora: datetime
    codigo: str
    cantidad: int
    total: float

    def __str__(self) -> str:
        """Retorna el resumen de la venta."""
        return f'{self.cantidad} x {self.codigo}: Q{self.total:.2f}'

    def __repr__(self) -> str:
        """Retorna la representación detallada de la venta."""
        return f'Venta({self.fecha_hora!r}, {self.codigo!r}, {self.cantidad!r}, {self.total!r})'
