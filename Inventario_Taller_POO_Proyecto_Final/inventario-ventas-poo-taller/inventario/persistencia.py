"""Carga y guardado CSV y registro de acciones del taller."""
import csv
from datetime import datetime
from pathlib import Path
from .modelos import Producto, Venta
from .inventario import Inventario
from .excepciones import InventarioError, PersistenciaError

class RepositorioCSV:
    """Administra archivos CSV de inventario y ventas."""
    CAMPOS_PRODUCTOS = ('codigo', 'nombre', 'categoria', 'precio', 'stock')
    CAMPOS_VENTAS = ('fecha_hora', 'codigo', 'cantidad', 'total')

    def __init__(self, ruta_inventario: Path):
        """Determina las rutas de inventario y ventas en un directorio común."""
        self._ruta_inventario = Path(ruta_inventario)
        self._ruta_ventas = self._ruta_inventario.with_name('ventas.csv')

    def cargar_productos(self) -> Inventario:
        """Lee productos del CSV; crea el archivo vacío si no existe; lanza PersistenciaError ante fallas."""
        inventario = Inventario()
        try:
            if not self._ruta_inventario.exists():
                self.guardar_productos(inventario)
            with self._ruta_inventario.open('r', newline='', encoding='utf-8-sig') as archivo:
                lector = csv.DictReader(archivo)
                if lector.fieldnames is None or set(self.CAMPOS_PRODUCTOS) - set(lector.fieldnames):
                    raise PersistenciaError('El archivo CSV de productos no tiene los encabezados correctos.')
                for numero, fila in enumerate(lector, 2):
                    try:
                        inventario.agregar(Producto.desde_fila_csv(fila))
                    except InventarioError as error:
                        raise PersistenciaError(f'Producto inválido en línea {numero}: {error}') from error
        except (OSError, csv.Error, UnicodeError) as error:
            raise PersistenciaError(f'No se pudo cargar inventario: {error}') from error
        return inventario

    def guardar_productos(self, inventario: Inventario) -> None:
        """Sobrescribe el inventario CSV; lanza PersistenciaError si falla."""
        try:
            self._ruta_inventario.parent.mkdir(parents=True, exist_ok=True)
            with self._ruta_inventario.open('w', newline='', encoding='utf-8') as archivo:
                escritor = csv.DictWriter(archivo, fieldnames=self.CAMPOS_PRODUCTOS)
                escritor.writeheader()
                for producto in inventario:
                    escritor.writerow(producto.a_fila_csv())
        except OSError as error:
            raise PersistenciaError(f'No se pudo guardar inventario: {error}') from error

    def cargar_ventas(self) -> list[Venta]:
        """Obtiene el historial de ventas guardado; retorna lista vacía si no existe."""
        if not self._ruta_ventas.exists():
            return []
        ventas = []
        try:
            with self._ruta_ventas.open('r', newline='', encoding='utf-8-sig') as archivo:
                lector = csv.DictReader(archivo)
                if lector.fieldnames is None or set(self.CAMPOS_VENTAS) - set(lector.fieldnames):
                    raise PersistenciaError('El CSV de ventas no tiene los encabezados correctos.')
                for fila in lector:
                    ventas.append(Venta(datetime.fromisoformat(fila['fecha_hora']), fila['codigo'], int(fila['cantidad']), float(fila['total'])))
        except (OSError, ValueError, KeyError, csv.Error) as error:
            raise PersistenciaError(f'No se pudo leer ventas: {error}') from error
        return ventas

    def guardar_venta(self, venta: Venta) -> None:
        """Anexa una venta al CSV, creando encabezados cuando no existía el archivo."""
        try:
            self._ruta_ventas.parent.mkdir(parents=True, exist_ok=True)
            nuevo = not self._ruta_ventas.exists() or self._ruta_ventas.stat().st_size == 0
            with self._ruta_ventas.open('a', newline='', encoding='utf-8') as archivo:
                escritor = csv.DictWriter(archivo, fieldnames=self.CAMPOS_VENTAS)
                if nuevo:
                    escritor.writeheader()
                escritor.writerow({'fecha_hora': venta.fecha_hora.isoformat(timespec='minutes'), 'codigo': venta.codigo,
                                  'cantidad': venta.cantidad, 'total': f'{venta.total:.2f}'})
        except OSError as error:
            raise PersistenciaError(f'No se pudo registrar venta: {error}') from error

class Bitacora:
    """Registra eventos con marca de tiempo sin sobrescribir eventos anteriores."""
    def __init__(self, ruta: Path):
        """Fija la ubicación del archivo de registro."""
        self._ruta = Path(ruta)

    def registrar(self, accion: str) -> None:
        """Añade una operación al archivo con fecha/hora; lanza PersistenciaError ante fallas."""
        try:
            self._ruta.parent.mkdir(parents=True, exist_ok=True)
            with self._ruta.open('a', encoding='utf-8') as archivo:
                archivo.write(f'[{datetime.now():%Y-%m-%d %H:%M:%S}] {accion}\n')
        except OSError as error:
            raise PersistenciaError(f'No se pudo escribir bitácora: {error}') from error
