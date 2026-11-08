"""Errores específicos para operaciones del inventario."""
class InventarioError(Exception):
    """Base de los errores controlables del sistema."""
class CodigoInvalidoError(InventarioError):
    """El código del repuesto no tiene el formato solicitado."""
class ProductoNoEncontradoError(InventarioError):
    """No existe un repuesto con el código recibido."""
class StockInsuficienteError(InventarioError):
    """La cantidad supera las existencias disponibles."""
class ProductoDuplicadoError(InventarioError):
    """El código ya pertenece a otro producto."""
class DatoInvalidoError(InventarioError):
    """Los datos de entrada incumplen una validación."""
class PersistenciaError(InventarioError):
    """No fue posible leer o guardar un archivo."""
