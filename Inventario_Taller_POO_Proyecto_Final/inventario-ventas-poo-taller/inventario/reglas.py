"""Jerarquía abstracta de reglas de aviso de existencias."""
from abc import ABC, abstractmethod
from .modelos import Producto

class ReglaStock(ABC):
    """Contrato para evaluar avisos relacionados con existencias."""
    def __init__(self, minimo: int = 3):
        """Configura el mínimo aceptable para la regla."""
        self._minimo = minimo

    @abstractmethod
    def evaluar(self, producto: Producto) -> str:
        """Retorna un mensaje de estado a partir del producto."""

class AlertaStockMinimo(ReglaStock):
    """Genera un aviso cuando las existencias son bajas."""
    def __init__(self, minimo: int = 3):
        """Define el umbral de alerta (tres unidades por defecto)."""
        super().__init__(minimo)

    def evaluar(self, producto: Producto) -> str:
        """Retorna la alerta cuando las unidades están en el umbral o por debajo."""
        if producto.necesita_reabastecer(self._minimo):
            return f'ALERTA DE STOCK: {producto.nombre} tiene {producto.stock} unidades restantes.'
        return ''

class EstadoStock(ReglaStock):
    """Presenta el estado del producto en el listado general."""
    def __init__(self, minimo: int = 3):
        """Reutiliza el mismo umbral para el estado del inventario."""
        super().__init__(minimo)

    def evaluar(self, producto: Producto) -> str:
        """Devuelve Stock bajo u OK usando la misma interfaz polimórfica."""
        return 'Stock bajo' if producto.necesita_reabastecer(self._minimo) else 'OK'
