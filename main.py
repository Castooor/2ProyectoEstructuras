from ArbolDirectorios import ArbolDirectorios
from auditoria import Auditoria
from TablaHash import TablaHash


# ============================================================
# MENÚ PRINCIPAL
# ============================================================

def mostrar_menu(tabla_hash):
    print("\n========================================")
    print(" SISTEMA DE ARCHIVOS DISTRIBUIDO")
    print("========================================")

    if tabla_hash.haySesionActiva():
        usuario = tabla_hash.usuarioActivo
        print(f" Usuario: {usuario.nombre} | Rol: {usuario.rol}")
    else:
        print(" Usuario: No hay sesión activa")

    print("----------------------------------------")
    print("1. Crear carpeta")
    print("2. Crear archivo")
    print("3. Buscar archivo")
    print("4. Mostrar árbol")
    print("5. Eliminar archivo")
    print("6. Eliminar carpeta")
    print("7. Cambiar directorio")
    print("8. Mostrar ruta actual")
    print("----------------------------------------")
    print("9. Registrar usuario")
    print("10. Iniciar sesión")
    print("11. Cerrar sesión")
    print("12. Mostrar usuario activo")
    print("13. Mostrar tabla hash")
    print("14. Demostrar colisiones")
    print("----------------------------------------")
    print("15. Ver auditoría")
    print("0. Salir")
    print("========================================")


# ============================================================
# ÁRBOL DE DIRECTORIOS
# ============================================================

def crear_carpeta(arbol, auditoria):
    nombre = input("Nombre de la carpeta: ").strip()

    destino = input(
        "Ruta de destino (Enter para el directorio actual): "
    ).strip()

    if destino == "":
        destino = None

    try:
        resultado = arbol.crearCarpeta(
            nombre,
            destino=destino,
            registrar_evento=auditoria.registrar
        )

        if resultado is not None:
            print(f"\n[OK] {arbol.ultimo_mensaje}")
        else:
            print(f"\n[ERROR] {arbol.ultimo_mensaje}")

    except ValueError as error:
        print(f"\n[ERROR] {error}")


def crear_archivo(arbol, auditoria):
    nombre = input("Nombre del archivo: ").strip()

    destino = input(
        "Ruta de destino (Enter para el directorio actual): "
    ).strip()

    contenido = input("Contenido del archivo: ")

    if destino == "":
        destino = None

    try:
        resultado = arbol.crearArchivo(
            nombre,
            destino=destino,
            contenido=contenido,
            registrar_evento=auditoria.registrar
        )

        if resultado is not None:
            print(f"\n[OK] {arbol.ultimo_mensaje}")
        else:
            print(f"\n[ERROR] {arbol.ultimo_mensaje}")

    except ValueError as error:
        print(f"\n[ERROR] {error}")


def buscar_archivo(arbol):
    nombre = input("Nombre del archivo a buscar: ").strip()

    resultado = arbol.buscarArchivo(nombre)

    if resultado is not None:
        print("\n========== ARCHIVO ENCONTRADO ==========")
        print(f"Nombre: {resultado.nombre}")
        print(f"Ruta: {resultado.obtenerRuta()}")
        print("========================================")
    else:
        print(f"\n[NO ENCONTRADO] {arbol.ultimo_mensaje}")


def mostrar_arbol(arbol):
    print("\n========== ÁRBOL DE DIRECTORIOS ==========")

    try:
        arbol.mostrarArbol(estilo="arbol")
    except TypeError:
        arbol.mostrarArbol()

    print("===========================================")


def eliminar_elemento(arbol, auditoria, tipo):
    ruta = input(
        f"Ruta del {tipo} a eliminar: "
    ).strip()

    if ruta == "":
        print("\n[ERROR] Debe ingresar una ruta.")
        return

    nodo = arbol.resolverNodo(ruta)

    if nodo is None:
        print("\n[ERROR] El elemento no existe.")
        return

    if tipo == "archivo" and not nodo.esArchivo():
        print(
            "\n[ERROR] La ruta indicada no corresponde a un archivo."
        )
        return

    if tipo == "carpeta" and not nodo.esCarpeta():
        print(
            "\n[ERROR] La ruta indicada no corresponde a una carpeta."
        )
        return

    resultado = arbol.eliminar(
        ruta,
        registrar_evento=auditoria.registrar
    )

    if resultado:
        print(f"\n[OK] {arbol.ultimo_mensaje}")
    else:
        print(f"\n[ERROR] {arbol.ultimo_mensaje}")


def cambiar_directorio(arbol):
    ruta = input("Ruta del directorio: ").strip()

    resultado = arbol.cambiarDirectorio(ruta)

    if resultado:
        print(
            f"\n[OK] Directorio actual: "
            f"{arbol.obtenerRutaActual()}"
        )
    else:
        print(f"\n[ERROR] {arbol.ultimo_mensaje}")


def mostrar_ruta_actual(arbol):
    ruta = arbol.obtenerRutaActual()

    print("\n========== RUTA ACTUAL ==========")
    print(f"Directorio actual: {ruta}")
    print("=================================")


# ============================================================
# AUTENTICACIÓN / TABLA HASH
# ============================================================

def registrar_usuario(tabla_hash, auditoria):
    print("\n========== REGISTRAR USUARIO ==========")

    nombre = input("Nombre de usuario: ").strip()
    contrasena = input("Contraseña: ").strip()

    print("\nRoles disponibles:")
    print("1. usuario")
    print("2. administrador")

    opcion_rol = input("Seleccione el rol: ").strip()

    if opcion_rol == "2":
        rol = "administrador"
    else:
        rol = "usuario"

    try:
        resultado = tabla_hash.registrarUsuario(
            nombre,
            contrasena,
            rol,
            registrar_evento=auditoria.registrar
        )

        if resultado:
            print(f"\n[OK] {tabla_hash.ultimo_mensaje}")
        else:
            print(f"\n[ERROR] {tabla_hash.ultimo_mensaje}")

    except ValueError as error:
        print(f"\n[ERROR] {error}")


def iniciar_sesion(tabla_hash, auditoria):
    print("\n========== INICIAR SESIÓN ==========")

    nombre = input("Usuario: ").strip()
    contrasena = input("Contraseña: ").strip()

    resultado = tabla_hash.iniciarSesion(
        nombre,
        contrasena,
        registrar_evento=auditoria.registrar
    )

    if resultado:
        usuario = tabla_hash.usuarioActivo

        print("\n[OK] Sesión iniciada correctamente.")
        print(f"Usuario: {usuario.nombre}")
        print(f"Rol: {usuario.rol}")
    else:
        print(f"\n[ERROR] {tabla_hash.ultimo_mensaje}")


def cerrar_sesion(tabla_hash, auditoria):
    resultado = tabla_hash.cerrarSesion(
        registrar_evento=auditoria.registrar
    )

    if resultado is not None:
        print(f"\n[OK] Sesión cerrada: {resultado}")
    else:
        print("\n[INFO] No hay ninguna sesión activa.")


def mostrar_usuario_activo(tabla_hash):
    print("\n========== USUARIO ACTIVO ==========")

    if tabla_hash.haySesionActiva():
        usuario = tabla_hash.usuarioActivo

        print(f"Usuario: {usuario.nombre}")
        print(f"Rol: {usuario.rol}")
    else:
        print("No hay ninguna sesión activa.")

    print("====================================")


def mostrar_tabla_hash(tabla_hash):
    print("\n")
    tabla_hash.mostrarTabla()


# ============================================================
# DEMOSTRACIÓN DE COLISIONES
# ============================================================

def buscar_nombres_colision(tabla_hash, nombre_base, cantidad=3):
    indice = tabla_hash.funcionHash(nombre_base)

    encontrados = []
    contador = 1

    while len(encontrados) < cantidad and contador <= 20000:
        candidato = f"{nombre_base}{contador}"

        if tabla_hash.funcionHash(candidato) == indice:
            encontrados.append(candidato)

        contador += 1

    return indice, encontrados


def demostrar_colisiones(tabla_hash, auditoria):
    print("\n========== DEMOSTRACIÓN DE COLISIONES ==========")

    nombre_base = input(
        "Nombre base para buscar colisiones "
        "(Enter = santiago): "
    ).strip()

    if nombre_base == "":
        nombre_base = "santiago"

    indice, colisionados = buscar_nombres_colision(
        tabla_hash,
        nombre_base,
        cantidad=3
    )

    print(
        f"\nEl usuario '{nombre_base}' produce el índice {indice}."
    )

    if not colisionados:
        print("[ERROR] No se encontraron colisiones.")
        return

    print("\nColisiones encontradas:")

    for nombre in colisionados:
        print(
            f"  {nombre} -> índice "
            f"{tabla_hash.funcionHash(nombre)}"
        )

    print("\nEstas son colisiones reales porque producen")
    print("el mismo índice en la tabla hash.")

    registrar = input(
        "\n¿Desea registrarlos para demostrar "
        "el encadenamiento? (s/n): "
    ).strip().lower()

    if registrar != "s":
        return

    for nombre in colisionados:
        if nombre not in tabla_hash:
            tabla_hash.registrarUsuario(
                nombre,
                "clave123",
                "usuario",
                registrar_evento=auditoria.registrar
            )

    cadena = tabla_hash.obtenerCadena(indice)

    print("\n========== CADENA DE COLISIÓN ==========")
    print(f"Índice: {indice}")
    print(" -> ".join(cadena))
    print("=========================================")


# ============================================================
# AUDITORÍA
# ============================================================

def mostrar_auditoria(auditoria):
    print("\n========== AUDITORÍA ==========")
    auditoria.mostrar_logs()
    print("===============================")


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():
    auditoria = Auditoria()
    arbol = ArbolDirectorios()
    tabla_hash = TablaHash()

    print("========================================")
    print(" SISTEMA DE ARCHIVOS DISTRIBUIDO")
    print("========================================")
    print("\nSistema iniciado correctamente.")
    print("Árbol de directorios: OK")
    print("Tabla hash: OK")
    print("Auditoría: OK")

    while True:
        mostrar_menu(tabla_hash)

        opcion = input("Seleccione una opción: ").strip()

        # ---------------- ÁRBOL ----------------

        if opcion == "1":
            crear_carpeta(arbol, auditoria)

        elif opcion == "2":
            crear_archivo(arbol, auditoria)

        elif opcion == "3":
            buscar_archivo(arbol)

        elif opcion == "4":
            mostrar_arbol(arbol)

        elif opcion == "5":
            eliminar_elemento(
                arbol,
                auditoria,
                "archivo"
            )

        elif opcion == "6":
            eliminar_elemento(
                arbol,
                auditoria,
                "carpeta"
            )

        elif opcion == "7":
            cambiar_directorio(arbol)

        elif opcion == "8":
            mostrar_ruta_actual(arbol)

        # ---------------- HASH ----------------

        elif opcion == "9":
            registrar_usuario(
                tabla_hash,
                auditoria
            )

        elif opcion == "10":
            iniciar_sesion(
                tabla_hash,
                auditoria
            )

        elif opcion == "11":
            cerrar_sesion(
                tabla_hash,
                auditoria
            )

        elif opcion == "12":
            mostrar_usuario_activo(tabla_hash)

        elif opcion == "13":
            mostrar_tabla_hash(tabla_hash)

        elif opcion == "14":
            demostrar_colisiones(
                tabla_hash,
                auditoria
            )

        # ---------------- AUDITORÍA ----------------

        elif opcion == "15":
            mostrar_auditoria(auditoria)

        # ---------------- SALIR ----------------

        elif opcion == "0":
            print("\nSaliendo del sistema...")
            break

        else:
            print(
                "\n[ERROR] Opción inválida."
            )


if __name__ == "__main__":
    main()