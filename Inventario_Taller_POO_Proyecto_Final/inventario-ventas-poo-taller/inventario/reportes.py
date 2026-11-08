"""Tablas alineadas de inventario y ventas."""
from datetime import date
from .modelos import Venta, Producto

class ReporteVentas:
    """Construye el reporte diario con columnas de ancho fijo."""
    def generar(self, ventas: list[Venta], dia: date | None = None) -> str:
        """Retorna el reporte de ventas del día indicado, o del día actual."""
        dia = dia or date.today()
        seleccion = [venta for venta in ventas if venta.fecha_hora.date() == dia]
        if not seleccion:
            return 'No se han registrado ventas en el día.'
        lineas = [f"{'FECHA/HORA':<18} {'CÓDIGO':<10} {'CANTIDAD':<10} {'TOTAL':<12}", '-' * 55]
        for venta in seleccion:
            fecha = venta.fecha_hora.strftime('%Y-%m-%d %H:%M')
            lineas.append(f'{fecha:<18} {venta.codigo:<10} {venta.cantidad:<10} Q{venta.total:<11.2f}')
        lineas.extend(['-' * 55, f'TOTAL RECAUDADO EN EL DÍA: Q{sum(v.total for v in seleccion):.2f}'])
        return '\n'.join(lineas)
