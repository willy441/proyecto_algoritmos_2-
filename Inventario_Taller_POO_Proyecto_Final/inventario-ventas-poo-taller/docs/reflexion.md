# Reflexión sobre la refactorización a POO

En el Proyecto 1, el inventario del taller funcionaba con listas de diccionarios y varias funciones separadas. Para el proyecto final, el cambio principal fue repartir esas tareas en clases. Se conserva el mismo negocio: repuestos de taller, registro de ventas, búsquedas, archivo CSV y aviso cuando quedan tres unidades o menos.

La clase `Producto` se encarga de sus propios datos y evita que se guarden precios negativos o existencias por debajo de cero. `Inventario` administra los productos sin preocuparse por el menú. `RepositorioCSV` realiza las lecturas y escrituras; `Bitacora` guarda los movimientos. Así resulta más sencillo localizar dónde hacer una corrección sin tocar todo el programa. `SistemaInventario` conecta estas piezas y recibe los datos del usuario.

La herencia se utiliza en las reglas de stock. `ReglaStock` define el método `evaluar` y sus subclases `AlertaStockMinimo` y `EstadoStock` lo implementan de formas distintas. Ambas reciben el mismo objeto `Producto`, pero una muestra un aviso después de una venta y la otra indica el estado dentro del listado. Esto permite agregar otra presentación del estado de stock sin reescribir el manejo del inventario.

Una dificultad importante fue corregir errores del archivo principal y sustituir las modificaciones directas de diccionarios por métodos que validan los cambios. También fue necesario mantener sincronizados el inventario y las ventas guardadas para que la información permaneciera disponible al reiniciar el programa. Las pruebas comprueban búsquedas, ventas, errores y persistencia.

**Uso de herramientas de apoyo:** [Completa aquí una declaración personal, precisa y honesta de las herramientas utilizadas, incluidas las de IA que correspondan, y de qué partes revisaste o modificaste tú].

> Revisa y adapta esta reflexión a lo que realmente hiciste y aprendiste antes de entregarla.
