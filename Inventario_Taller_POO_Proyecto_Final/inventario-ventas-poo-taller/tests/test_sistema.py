"""Pruebas automáticas de las funcionalidades y errores habituales."""
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from inventario.app import SistemaInventario
from inventario.modelos import Producto, Venta
from inventario.inventario import Inventario
from inventario.reglas import AlertaStockMinimo, EstadoStock
from inventario.excepciones import CodigoInvalidoError, StockInsuficienteError, ProductoNoEncontradoError, ProductoDuplicadoError
from inventario.reportes import ReporteVentas

class PruebasSistema(unittest.TestCase):
    """Prueba operaciones usando archivos temporales y sin modificar el CSV real."""
    def setUp(self):
        """Crea un directorio temporal y configura un sistema vacío."""
        self.tmp = tempfile.TemporaryDirectory()
        self.sistema = SistemaInventario(Path(self.tmp.name) / 'inventario.csv')
        self.sistema.iniciar()

    def tearDown(self):
        """Limpia los archivos generados por cada prueba."""
        self.tmp.cleanup()

    def test_alta_busqueda_y_ordenamiento(self):
        """Prueba alta, búsquedas sin mayúsculas y ordenamientos."""
        self.sistema.registrar_producto('REP011', 'Filtro de aire', 'Filtros', 85, 5)
        self.sistema.registrar_producto('REP012', 'Aceite 10w30', 'Lubricantes', 185, 4)
        self.assertEqual(len(self.sistema._inventario.buscar('filtro')), 1)
        self.assertEqual(self.sistema._inventario.ordenar('precio')[0].codigo, 'REP011')
        self.assertEqual(len(self.sistema._inventario.categorias()), 2)

    def test_venta_alerta_y_reporte(self):
        """Prueba venta, alerta de tres unidades y reporte diario."""
        self.sistema.registrar_producto('REP011', 'Filtro de aire', 'Filtros', 85, 5)
        venta = self.sistema.registrar_venta('REP011', 2)
        producto = self.sistema._inventario.obtener('REP011')
        self.assertEqual(producto.stock, 3)
        self.assertEqual(venta.total, 170)
        self.assertIn('ALERTA', AlertaStockMinimo().evaluar(producto))
        self.assertEqual(EstadoStock().evaluar(producto), 'Stock bajo')
        self.assertIn('170.00', ReporteVentas().generar(self.sistema._ventas))

    def test_error_stock_insuficiente(self):
        """Confirma que una venta imposible no descuenta unidades."""
        self.sistema.registrar_producto('REP011', 'Filtro de aire', 'Filtros', 85, 2)
        with self.assertRaises(StockInsuficienteError):
            self.sistema.registrar_venta('REP011', 3)
        self.assertEqual(self.sistema._inventario.obtener('REP011').stock, 2)

    def test_error_codigo_invalido(self):
        """Rechaza códigos que incumplen el formato de tres letras y tres números."""
        with self.assertRaises(CodigoInvalidoError):
            self.sistema.registrar_producto('RE-1', 'Filtro', 'Filtros', 85, 5)

    def test_error_no_encontrado_y_duplicado(self):
        """Comprueba errores propios al buscar un ausente o repetir código."""
        with self.assertRaises(ProductoNoEncontradoError):
            self.sistema._inventario.obtener('REP999')
        self.sistema.registrar_producto('REP011', 'Filtro', 'Filtros', 85, 5)
        with self.assertRaises(ProductoDuplicadoError):
            self.sistema.registrar_producto('REP011', 'Filtro', 'Filtros', 85, 5)

    def test_guardado_reinicio_y_eliminacion(self):
        """Comprueba persistencia CSV y la baja de un repuesto."""
        self.sistema.registrar_producto('REP011', 'Filtro', 'Filtros', 85, 5)
        reiniciado = SistemaInventario(Path(self.tmp.name) / 'inventario.csv')
        reiniciado.iniciar()
        self.assertEqual(reiniciado._inventario.obtener('REP011').stock, 5)
        reiniciado.eliminar_producto('REP011')
        self.assertNotIn('REP011', reiniciado._inventario)

if __name__ == '__main__':
    unittest.main()
