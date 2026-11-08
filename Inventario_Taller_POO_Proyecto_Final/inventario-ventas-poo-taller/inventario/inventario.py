"""Colección de repuestos y búsquedas de inventario."""
from .modelos import Producto
from .excepciones import ProductoDuplicadoError, ProductoNoEncontradoError

class Inventario:
    """Administra productos en un diccionario indexado por código."""
    def __init__(self):
        """Inicializa el inventario vacío."""
        self._productos: dict[str, Producto] = {}

    def agregar(self, producto: Producto) -> None:
        """Incorpora un producto; lanza ProductoDuplicadoError si existe su código."""
        if producto.codigo in self._productos:
            raise ProductoDuplicadoError(f'Ya existe un repuesto con código {producto.codigo}.')
        self._productos[producto.codigo] = producto

    def obtener(self, codigo: str) -> Producto:
        """Retorna un producto por código o lanza ProductoNoEncontradoError."""
        clave = codigo.strip().upper()
        if clave not in self._productos:
            raise ProductoNoEncontradoError(f'No existe el producto {clave}.')
        return self._productos[clave]

    def buscar(self, termino: str) -> list[Producto]:
        """Retorna coincidencias por código exacto o nombre parcial, sin distinguir mayúsculas."""
        consulta = termino.strip().casefold()
        if not consulta:
            return []
        return [p for p in self._productos.values() if p.codigo.casefold() == consulta or consulta in p.nombre.casefold()]

    def ordenar(self, criterio: str = 'nombre') -> list[Producto]:
        """Retorna productos ordenados por nombre o precio, sin modificar el diccionario."""
        if criterio == 'precio':
            return sorted(self._productos.values(), key=lambda p: (p.precio, p.nombre.casefold()))
        return sorted(self._productos.values(), key=lambda p: p.nombre.casefold())

    def categorias(self) -> set[str]:
        """Retorna las categorías únicas presentes en el inventario."""
        return {p.categoria for p in self._productos.values()}

    def eliminar(self, codigo: str) -> Producto:
        """Retira un producto y lo retorna; lanza ProductoNoEncontradoError si falta."""
        producto = self.obtener(codigo)
        del self._productos[producto.codigo]
        return producto

    def __len__(self) -> int:
        """Retorna el número de repuestos registrados."""
        return len(self._productos)

    def __contains__(self, codigo: str) -> bool:
        """Indica si el código está en el inventario."""
        return codigo.strip().upper() in self._productos

    def __iter__(self):
        """Permite recorrer los objetos Producto del inventario."""
        return iter(self._productos.values())
