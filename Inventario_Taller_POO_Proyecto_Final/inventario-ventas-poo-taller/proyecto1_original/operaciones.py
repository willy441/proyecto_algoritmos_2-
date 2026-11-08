"""
Módulo de operaciones para el Sistema de Inventario del Taller Automotriz.
Contiene la lógica de negocio, manejo de archivos y colecciones.
"""

import os
from datetime import datetime

# Archivos de persistencia
ARCHIVO_INVENTARIO = "inventario_taller.csv"
ARCHIVO_BITACORA = "bitacora.log"
STOCK_MINIMO_ALERTA = 3  # Regla de negocio: Alerta de stock mínimo


def registrar_bitacora(accion: str) -> None:
    """
    Registra una operación en el archivo de log (modo append) con fecha y hora.
    """
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{fecha_actual}] {accion}\n"
    # Manejo de error en escritura de bitácora
    try:
        with open(ARCHIVO_BITACORA, "a", encoding="utf-8") as archivo:
            archivo.write(linea)
    except OSError as err:
        print(f"Error al escribir en la bitácora: {err}")


def validar_codigo(codigo: str) -> bool:
    """
    Valida formato de código automotriz: 3 letras + 3 dígitos (Ej. REP001, ACE101).
    Usa métodos de cadenas: len(), isalpha(), isdigit().
    """
    codigo = codigo.strip().upper()
    if len(codigo) != 6:
        return False
    # Primeros 3 caracteres deben ser letras y los últimos 3 números
    prefijo = codigo[:3]
    sufijo = codigo[3:]
    return prefijo.isalpha() and sufijo.isdigit()


def cargar_inventario() -> list[dict]:
    """
    Carga el inventario desde el archivo CSV.
    Si el archivo no existe, lo crea con encabezados y 10 productos de muestra.
    Retorna una lista de diccionarios.
    """
    inventario = []

    # Si no existe, crear con 10 productos de ejemplo de taller mecánico
    if not os.path.exists(ARCHIVO_INVENTARIO):
        productos_iniciales = [
            "REP001,Filtro de Aceite Sintetico,Filtros,65.00,12\n",
            "REP002,Filtro de Aire Motor,Filtros,85.00,8\n",
            "REP003,Pastillas de Freno Delanteras,Frenos,250.00,5\n",
            "REP004,Liquido de Frenos DOT4,Frenos,45.00,2\n",  # Alerta stock
            "REP005,Bujias de Iridio (Pack 4),Encendido,320.00,6\n",
            "REP006,Aceite 10W-30 Galon,Lubricantes,185.00,10\n",
            "REP007,Aceite 20W-50 Galon,Lubricantes,160.00,3\n",  # Alerta stock
            "REP008,Amortiguadores Delanteros,Suspension,750.00,4\n",
            "REP009,Bateria 12V 13 Placas,Electrico,650.00,2\n",  # Alerta stock
            "REP010,Faja de Tiempo Gates,Motor,140.00,7\n",
        ]
        try:
            with open(ARCHIVO_INVENTARIO, "w", encoding="utf-8") as archivo:
                archivo.write("codigo,nombre,categoria,precio,stock\n")
                archivo.writelines(productos_iniciales)
            registrar_bitacora("Archivo creado con 10 productos iniciales del taller")
        except OSError as e:
            print(f"Error al inicializar el archivo: {e}")
            return []

    # Lectura del archivo
    try:
        with open(ARCHIVO_INVENTARIO, "r", encoding="utf-8") as archivo:
            lineas = archivo.readlines()
            for linea in lineas[1:]:  # Omitir fila de encabezados
                datos = linea.strip().split(",")
                if len(datos) == 5:
                    item = {
                        "codigo": datos[0].strip().upper(),
                        "nombre": datos[1].strip(),
                        "categoria": datos[2].strip(),
                        "precio": float(datos[3]),
                        "stock": int(datos[4]),
                    }
                    inventario.append(item)
    except (OSError, ValueError) as e:
        print(f"Error al leer archivo de inventario: {e}")

    return inventario


def guardar_inventario(inventario: list[dict]) -> None:
    """
    Sobrescribe el archivo CSV con la lista de productos actual.
    """
    try:
        with open(ARCHIVO_INVENTARIO, "w", encoding="utf-8") as archivo:
            archivo.write("codigo,nombre,categoria,precio,stock\n")
            for p in inventario:
                archivo.write(
                    f"{p['codigo']},{p['nombre']},{p['categoria']},{p['precio']:.2f},{p['stock']}\n"
                )
    except OSError as e:
        print(f"Error al guardar inventario: {e}")


def obtener_categorias(inventario: list[dict]) -> set:
    """
    Utiliza la estructura Set (conjunto) para devolver las categorías sin duplicados.
    """
    return {p["categoria"] for p in inventario}


def buscar_producto(inventario: list[dict], criterio: str) -> list[dict]:
    """
    Busca por código exacto o coincidencia parcial en nombre (sin distinguir mayúsculas).
    """
    busqueda = criterio.strip().lower()
    coincidencias = []
    for p in inventario:
        if busqueda == p["codigo"].lower() or busqueda in p["nombre"].lower():
            coincidencias.append(p)
    return coincidencias


def ordenar_inventario(inventario: list[dict], criterio: str) -> list[dict]:
    """
    Ordena la lista de productos utilizando sorted() y funciones lambda.
    Permite ordenar por 'nombre' o por 'precio'.
    """
    if criterio == "precio":
        return sorted(inventario, key=lambda x: x["precio"])
    return sorted(inventario, key=lambda x: x["nombre"].lower())
def eliminar_producto(inventario: list[dict], codigo: str) -> bool:
    """
    Busca un producto por su código y lo elimina de la lista en memoria.
    Retorna True si lo encontró y eliminó, o False si no existía.
    """
    codigo = codigo.strip().upper()
    for i, p in enumerate(inventario):
        if p["codigo"] == codigo:
            # Eliminamos el elemento de la lista usando pop() o del
            inventario.pop(i)
            return True
    return False
