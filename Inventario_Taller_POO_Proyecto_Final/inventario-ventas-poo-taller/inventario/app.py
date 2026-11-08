"""Interfaz de consola del taller y coordinación de operaciones."""
from datetime import datetime
from pathlib import Path
from .inventario import Inventario
from .modelos import Producto, Venta
from .reglas import ReglaStock, AlertaStockMinimo, EstadoStock
from .persistencia import RepositorioCSV, Bitacora
from .reportes import ReporteVentas
from .excepciones import InventarioError, DatoInvalidoError

class SistemaInventario:
    """Ejecuta el menú y coordina modelos, reglas, archivos y reportes."""
    STOCK_MINIMO = 3

    def __init__(self, ruta_csv: str | Path):
        """Configura dependencias; las rutas quedan relativas al CSV proporcionado."""
        self._repositorio = RepositorioCSV(Path(ruta_csv))
        self._bitacora = Bitacora(Path(ruta_csv).with_name('bitacora.log'))
        self._reglas: list[ReglaStock] = [AlertaStockMinimo(self.STOCK_MINIMO), EstadoStock(self.STOCK_MINIMO)]
        self._reporte = ReporteVentas()
        self._inventario = Inventario()
        self._ventas: list[Venta] = []

    def iniciar(self) -> None:
        """Carga los datos persistidos y mantiene el historial de ventas en memoria."""
        self._inventario = self._repositorio.cargar_productos()
        self._ventas = self._repositorio.cargar_ventas()

    def registrar_producto(self, codigo: str, nombre: str, categoria: str, precio: float, stock: int) -> Producto:
        """Añade un producto validado; propaga errores de datos o duplicación."""
        producto = Producto(codigo, nombre, categoria, precio, stock)
        self._inventario.agregar(producto)
        self._repositorio.guardar_productos(self._inventario)
        self._bitacora.registrar(f'Producto agregado: {producto.codigo} - {producto.nombre} (Stock: {producto.stock})')
        return producto

    def registrar_venta(self, codigo: str, cantidad: int) -> Venta:
        """Descuenta existencias, guarda la venta y retorna el registro inmutable."""
        producto = self._inventario.obtener(codigo)
        producto.descontar_stock(cantidad)
        venta = Venta(datetime.now(), producto.codigo, cantidad, producto.precio * cantidad)
        self._repositorio.guardar_productos(self._inventario)
        self._repositorio.guardar_venta(venta)
        self._ventas.append(venta)
        self._bitacora.registrar(f'Venta: {cantidad}x {producto.codigo} por Q{venta.total:.2f}')
        return venta

    def eliminar_producto(self, codigo: str) -> Producto:
        """Quita un repuesto por código y registra la baja."""
        producto = self._inventario.eliminar(codigo)
        self._repositorio.guardar_productos(self._inventario)
        self._bitacora.registrar(f'Producto eliminado: {producto.codigo} - {producto.nombre}')
        return producto

    def mostrar_productos(self, productos: list[Producto], con_estado: bool = False) -> None:
        """Muestra una tabla alineada; opcionalmente incluye el estado de stock."""
        cabecera = f"{'CÓDIGO':<8} {'REPUESTO':<34} {'CATEGORÍA':<16} {'PRECIO':<12} {'STOCK':<7}"
        if con_estado:
            cabecera += ' ESTADO'
        print(cabecera)
        print('-' * (95 if con_estado else 80))
        for p in productos:
            linea = f'{p.codigo:<8} {p.nombre[:34]:<34} {p.categoria[:16]:<16} Q{p.precio:<11.2f} {p.stock:<7}'
            if con_estado:
                linea += f' {self._reglas[1].evaluar(p)}'
            print(linea)

    def menu_agregar(self) -> None:
        """Pide los datos de un repuesto y lo almacena."""
        print('\n--- REGISTRAR NUEVO REPUESTO ---')
        codigo = input('Código (3 letras y 3 números): ')
        nombre = input('Nombre de la pieza: ')
        categoria = input('Categoría: ')
        try:
            precio = float(input('Precio unitario (Q): '))
            stock = int(input('Cantidad en stock: '))
        except ValueError as error:
            raise DatoInvalidoError('Precio y stock deben ser valores numéricos válidos.') from error
        producto = self.registrar_producto(codigo, nombre, categoria, precio, stock)
        print(f'>> Repuesto registrado: {producto}')

    def menu_buscar(self) -> None:
        """Busca repuestos por código o parte del nombre."""
        resultados = self._inventario.buscar(input('Ingrese código o nombre parcial: '))
        self.mostrar_productos(resultados) if resultados else print('>> No se encontraron repuestos.')

    def menu_venta(self) -> None:
        """Solicita una venta, muestra total y aplica la regla de stock mínimo."""
        codigo = input('Código del repuesto a vender: ').strip()
        producto = self._inventario.obtener(codigo)
        try:
            cantidad = int(input(f'Cantidad (disponibles: {producto.stock}): '))
        except ValueError as error:
            raise DatoInvalidoError('La cantidad debe ser un número entero.') from error
        venta = self.registrar_venta(codigo, cantidad)
        print(f'>> Venta completada. Total: Q{venta.total:.2f}')
        aviso = self._reglas[0].evaluar(producto)
        if aviso:
            print(f'>> {aviso}')

    def menu_inventario(self) -> None:
        """Muestra categorías y repuestos ordenados por nombre o precio."""
        opcion = input('Ordenar por: 1. Nombre | 2. Precio: ').strip()
        criterio = 'precio' if opcion == '2' else 'nombre'
        print('Categorías:', ', '.join(sorted(self._inventario.categorias())))
        self.mostrar_productos(self._inventario.ordenar(criterio), con_estado=True)

    def menu_reporte(self) -> None:
        """Imprime las ventas realizadas durante el día de hoy."""
        print('\n--- REPORTE DE VENTAS DEL DÍA ---')
        print(self._reporte.generar(self._ventas))

    def menu_eliminar(self) -> None:
        """Confirma y retira un repuesto existente."""
        producto = self._inventario.obtener(input('Código a retirar: '))
        if input(f'¿Eliminar {producto.nombre}? (s/n): ').strip().casefold() == 's':
            self.eliminar_producto(producto.codigo)
            print('>> Repuesto eliminado.')
        else:
            print('>> Operación cancelada.')

    def ejecutar(self) -> None:
        """Muestra el menú hasta salir; captura los errores esperados sin traceback."""
        try:
            self.iniciar()
        except InventarioError as error:
            print(f'>> Error al iniciar: {error}')
            return
        acciones = {'1': self.menu_agregar, '2': self.menu_buscar, '3': self.menu_venta,
                    '4': self.menu_inventario, '5': self.menu_reporte, '7': self.menu_eliminar}
        while True:
            print('\n=== SISTEMA DE INVENTARIO - TALLER AUTOMOTRIZ ===')
            print('1. Agregar repuesto\n2. Buscar repuesto\n3. Registrar venta\n4. Mostrar inventario'
                  '\n5. Reporte de ventas del día\n6. Salir y guardar\n7. Eliminar repuesto')
            try:
                opcion = input('Seleccione opción (1-7): ').strip()
                if opcion == '6':
                    self._repositorio.guardar_productos(self._inventario)
                    self._bitacora.registrar('Cierre de sistema y datos guardados')
                    print('>> Datos guardados. Hasta luego.')
                    break
                accion = acciones.get(opcion)
                if accion is None:
                    print('>> Opción inválida.')
                    continue
                accion()
            except InventarioError as error:
                print(f'>> Error: {error}')
            except (EOFError, KeyboardInterrupt):
                print('\n>> Sesión interrumpida; el inventario ya se guardó tras cada modificación.')
                break
