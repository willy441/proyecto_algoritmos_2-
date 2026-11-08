"""
Programa Principal: Sistema de Inventario y Ventas - Taller Automotriz
Curso de Algoritmos - UMG
"""

from datetime import datetime
from operaciones import (
    STOCK_MINIMO_ALERTA,
    buscar_producto,
    cargar_inventario,
    guardar_inventario,
    obtener_categorias,
    registrar_bitacora,
    validar_codigo,eliminar_productoq
)

# Estructura para registrar ventas de la sesión: Lista de tuplas (inmutables)
# Formato: (fecha_hora, codigo, cantidad, total)
registro_ventas_dia: list[tuple] = []


def menu_agregar_producto(inventario: list[dict]) -> None:
    print("\n--- REGISTRAR NUEVO REPUESTO / SERVICIO ---")
    codigo = input("Ingrese código (Ej. REP011 - 3 letras y 3 números): ").strip().upper()

    if not validar_codigo(codigo):
        print(">> Error: Formato de código inválido (debe tener 3 letras y 3 dígitos).")
        return

    # Verificar existencia
    if any(p["codigo"] == codigo for p in inventario):
        print(">> Error: Ya existe un repuesto con ese código.")
        return

    nombre = input("Nombre de la pieza/repuesto: ").strip().title()
    categoria = input("Categoría (Frenos, Filtros, Lubricantes, etc.): ").strip().capitalize()

    # Manejo de error en conversión de tipos numéricos
    try:
        precio = float(input("Precio unitario (Q): "))
        stock = int(input("Cantidad inicial en stock: "))
        if precio <= 0 or stock < 0:
            print(">> Error: Precio y stock deben ser mayores a cero.")
            return
    except ValueError:
        print(">> Error: Debe ingresar valores numéricos válidos.")
        return

    nuevo = {
        "codigo": codigo,
        "nombre": nombre,
        "categoria": categoria,
        "precio": precio,
        "stock": stock,
    }
    inventario.append(nuevo)
    registrar_bitacora(f"Producto agregado: {codigo} - {nombre} (Stock: {stock})")
    print(f">> Repuesto '{nombre}' registrado exitosamente.")


def menu_buscar_producto(inventario: list[dict]) -> None:
    print("\n--- BÚSQUEDA DE REPUESTO ---")
    termino = input("Ingrese código o parte del nombre a buscar: ")
    resultados = buscar_producto(inventario, termino)

    if not resultados:
        print(">> No se encontraron piezas que coincidan con la búsqueda.")
        return

    print("\nResultados encontrados:")
    print(f"{'CÓDIGO':<8} {'REPUESTO':<32} {'CATEGORÍA':<15} {'PRECIO':<10} {'STOCK':<6}")
    print("-" * 75)
    for p in resultados:
        print(f"{p['codigo']:<8} {p['nombre']:<32} {p['categoria']:<15} Q{p['precio']:<9.2f} {p['stock']:<6}")


def menu_registrar_venta(inventario: list[dict]) -> None:
    print("\n--- REGISTRAR VENTA / SALIDA DE TALLER ---")
    codigo = input("Código del repuesto a vender: ").strip().upper()

    producto_encontrado = None
    for p in inventario:
        if p["codigo"] == codigo:
            producto_encontrado = p
            break

    if not producto_encontrado:
        print(">> Error: El código ingresado no existe en el inventario.")
        return

    try:
        cantidad = int(input(f"Cantidad a vender (Disponibles: {producto_encontrado['stock']}): "))
    except ValueError:
        print(">> Error: La cantidad debe ser un número entero.")
        return

    if cantidad <= 0:
        print(">> Error: La cantidad debe ser mayor a 0.")
        return

    # Validación de stock disponible
    if cantidad > producto_encontrado["stock"]:
        print(f">> Error: Stock insuficiente. Solo hay {producto_encontrado['stock']} unidades.")
        return

    # Aplicar venta
    producto_encontrado["stock"] -= cantidad
    total = cantidad * producto_encontrado["precio"]
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Registro inmutable usando tupla
    venta_registro = (fecha_hora, codigo, cantidad, total)
    registro_ventas_dia.append(venta_registro)

    registrar_bitacora(f"Venta: {cantidad}x {codigo} por un total de Q{total:.2f}")
    print(f">> Venta completada con éxito. Total cobrado: Q{total:.2f}")

    # Regla de negocio: Alerta de stock mínimo
    if producto_encontrado["stock"] <= STOCK_MINIMO_ALERTA:
        print(f"⚠️ [ALERTA DE STOCK]: El repuesto '{producto_encontrado['nombre']}' tiene {producto_encontrado['stock']} unidades restantes.")


def menu_mostrar_inventario(inventario: list[dict]) -> None:
    print("\n--- INVENTARIO GENERAL ---")
    print("Opciones de ordenamiento: 1. Por Nombre | 2. Por Precio")
    opc = input("Seleccione criterio (1 o 2): ").strip()

    criterio = "precio" if opc == "2" else "nombre"
    from operaciones import ordenar_inventario
    lista_ordenada = ordenar_inventario(inventario, criterio)

    print(f"\nCategorías activas registradas: {', '.join(obtener_categorias(inventario))}")
    print(f"{'CÓDIGO':<8} {'REPUESTO':<32} {'CATEGORÍA':<15} {'PRECIO':<10} {'STOCK':<8} {'ESTADO'}")
    print("-" * 85)
    for p in lista_ordenada:
        alerta = "⚠️ Stock bajo" if p["stock"] <= STOCK_MINIMO_ALERTA else "OK"
        print(f"{p['codigo']:<8} {p['nombre']:<32} {p['categoria']:<15} Q{p['precio']:<9.2f} {p['stock']:<8} {alerta}")


def menu_reporte_ventas() -> None:
    print("\n================== REPORTE DE VENTAS DEL DÍA ==================")
    if not registro_ventas_dia:
        print("No se han registrado ventas en esta sesión.")
        return

    # Encabezados con formato alineado f-strings
    print(f"{'FECHA/HORA':<18} {'CÓDIGO':<10} {'CANTIDAD':<10} {'TOTAL':<12}")
    print("-" * 55)

    gran_total = 0.0
    for venta in registro_ventas_dia:
        # Desempaquetado de tupla: (fecha, cod, cant, tot)
        fecha, cod, cant, tot = venta
        print(f"{fecha:<18} {cod:<10} {cant:<10} Q{tot:<11.2f}")
        gran_total += tot

    print("-" * 55)
    print(f"TOTAL RECAUDADO EN EL DÍA: Q{gran_total:.2f}")
    def menu_eliminar_producto(inventario: list[dict]) -> None:
    print("\n--- DAR DE BAJA / QUITAR REPUESTO DEL INVENTARIO ---")
    codigo = input("Ingrese el código del producto a retirar (Ej. REP001): ").strip().upper()

    # Buscamos si existe para mostrar el nombre antes de borrar
    producto = next((p for p in inventario if p["codigo"] == codigo), None)

    if not producto:
        print(">> Error: No se encontró ningún producto con ese código.")
        return

    # Confirmación de seguridad
    confirmacion = input(f"¿Seguro que desea eliminar '{producto['nombre']}'? (s/n): ").strip().lower()
    if confirmacion == "s":
        if eliminar_producto(inventario, codigo):
            registrar_bitacora(f"Producto eliminado/dado de baja: {codigo} - {producto['nombre']}")
            print(f">> El repuesto '{producto['nombre']}' ha sido retirado del sistema.")
    else:
        print(">> Operación cancelada.")


def main():
    inventario = cargar_inventario()

    while True:
        print("\n==============================================")
        print("   SISTEMA DE INVENTARIO - TALLER AUTOMOTRIZ  ")
        print("==============================================")
        print("1. Agregar nuevo producto/repuesto")
        print("2. Buscar producto (código o nombre)")
        print("3. Registrar venta de repuesto")
        print("4. Mostrar inventario completo")
        print("5. Generar reporte de ventas del día")
        print("6. Salir y guardar cambios")
        print("==============================================")

        opcion = input("Seleccione una opción (1-6): ").strip()

        if opcion == "1":
            menu_agregar_producto(inventario)
        elif opcion == "2":
            menu_buscar_producto(inventario)
        elif opcion == "3":
            menu_registrar_venta(inventario)
        elif opcion == "4":
            menu_mostrar_inventario(inventario)
        elif opcion == "5":
            menu_reporte_ventas()
        elif opcion == "6":
            guardar_inventario(inventario)
            registrar_bitacora("Cierre de sistema y datos guardados correctamente")
            print("\n>> Datos guardados en archivo. Saliendo del sistema...")
            break
        else:
            print(">> Opción inválida. Intente de nuevo.")


if __name__ == "__main__":
    main()
