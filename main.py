from ArbolDirectorios import ArbolDirectorios
from auditoria import Auditoria
from TablaHash import TablaHash
from GrafoServidores import GrafoServidores
from MenuGrafos import menu_grafos
from collections import namedtuple
import os


# Archivos de persistencia (junto a main.py, sin importar desde dónde se ejecute).
CARPETA_DATOS = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_USUARIOS = os.path.join(CARPETA_DATOS, "usuarios.json")
ARCHIVO_RED = os.path.join(CARPETA_DATOS, "red_servidores.json")

# Cuenta que se crea solo la primera vez (cuando no hay usuarios guardados)
# para poder iniciar sesión. Después los usuarios se leen de usuarios.json.
ADMIN_INICIAL_USUARIO = "admin"
ADMIN_INICIAL_CONTRASENA = "admin123"

# Una acción del menú. 'solo_admin' indica si el rol "usuario" la tiene vedada.
Accion = namedtuple("Accion", ["grupo", "descripcion", "ejecutar", "solo_admin"])


# ============================================================
# MENÚ PRINCIPAL
# ============================================================

def mostrar_menu_inicio():
    print("\n========================================")
    print(" SISTEMA DE ARCHIVOS DISTRIBUIDO")
    print("========================================")
    print("1. Iniciar sesión")
    print("2. Salir")
    print("========================================")


def mostrar_menu_rol(tabla_hash, disponibles):
    """Dibuja el menú de la sesión activa con las acciones de su rol."""
    usuario = tabla_hash.usuarioActivo

    print("\n========================================")
    print(" SISTEMA DE ARCHIVOS DISTRIBUIDO")
    print("========================================")
    print(f" Usuario: {usuario.nombre} | Rol: {usuario.rol}")

    grupo_actual = None
    for numero, accion in enumerate(disponibles, start=1):
        if accion.grupo != grupo_actual:
            grupo_actual = accion.grupo
            print(f"---------- {grupo_actual} ----------")
        print(f"{numero}. {accion.descripcion}")

    print("----------------------------------------")
    print("0. Cerrar sesión")
    print("========================================")


# ============================================================
# ÁRBOL DE DIRECTORIOS
# ============================================================

def exigir_administrador(tabla_hash, auditoria, accion):
    """Devuelve True si la sesión activa es administrador.

    Si no lo es, muestra el motivo y registra el intento denegado en la
    auditoría. Se llama ANTES de pedir datos, para no hacer escribir al
    usuario algo que luego se va a rechazar.
    """
    if tabla_hash.verificarPermiso(accion, registrar_evento=auditoria.registrar):
        return True

    print(f"\n[ACCESO DENEGADO] {tabla_hash.ultimo_mensaje}")
    if not tabla_hash.haySesionActiva():
        print("Inicie sesión con un administrador (opción 10).")
    return False


def crear_carpeta(arbol, auditoria, tabla_hash):
    if not exigir_administrador(tabla_hash, auditoria, "crear carpeta"):
        return

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


def crear_archivo(arbol, auditoria, tabla_hash):
    if not exigir_administrador(tabla_hash, auditoria, "crear archivo"):
        return

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


def eliminar_elemento(arbol, auditoria, tabla_hash, tipo):
    if not exigir_administrador(tabla_hash, auditoria, f"eliminar {tipo}"):
        return

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


def eliminar_usuario(tabla_hash, auditoria):
    print("\n========== ELIMINAR USUARIO ==========")

    nombre = input("Nombre de usuario a eliminar: ").strip()

    if nombre == "":
        print("\n[ERROR] Debe ingresar un nombre de usuario.")
        return

    objetivo = tabla_hash.buscarUsuario(nombre)

    if objetivo is None:
        print(f"\n[ERROR] El usuario '{nombre}' no existe.")
        return

    # Un administrador no puede borrar su propia cuenta con la sesión abierta.
    # Así siempre queda al menos un administrador y nadie se queda sin acceso.
    if objetivo is tabla_hash.usuarioActivo:
        print("\n[ERROR] No puede eliminar la cuenta con la que tiene la sesión abierta.")
        return

    confirmar = input(
        f"¿Eliminar al usuario '{objetivo.nombre}' (rol {objetivo.rol})? (s/n): "
    ).strip().lower()

    if confirmar != "s":
        print("\n[INFO] Operación cancelada.")
        return

    if tabla_hash.eliminarUsuario(nombre, registrar_evento=auditoria.registrar):
        print(f"\n[OK] {tabla_hash.ultimo_mensaje}")
    else:
        print(f"\n[ERROR] {tabla_hash.ultimo_mensaje}")


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
        return True

    # Mensaje genérico: no revela si el usuario existe o si falló la contraseña
    # (la auditoría sí guarda el motivo exacto).
    print("\n[ERROR] Usuario o contraseña incorrectos.")
    return False


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
# ACCESO POR ROL
# ============================================================

def definir_acciones(arbol, tabla_hash, auditoria, red):
    """Lista de todas las acciones del sistema y quién puede usarlas.

    El administrador ve todas. El rol 'usuario' solo ve las que tienen
    solo_admin=False (consultas); las delicadas (crear/borrar archivos y
    carpetas, registrar/borrar usuarios, tabla hash, auditoría y modificar
    la red) no aparecen en su menú.
    """

    def red_y_enrutamiento():
        menu_grafos(
            red,
            registrar=auditoria.registrar,
            solo_lectura=not tabla_hash.esAdministrador()
        )

    return [
        Accion("ARCHIVOS", "Crear carpeta",
               lambda: crear_carpeta(arbol, auditoria, tabla_hash), True),
        Accion("ARCHIVOS", "Crear archivo",
               lambda: crear_archivo(arbol, auditoria, tabla_hash), True),
        Accion("ARCHIVOS", "Buscar archivo",
               lambda: buscar_archivo(arbol), False),
        Accion("ARCHIVOS", "Mostrar árbol",
               lambda: mostrar_arbol(arbol), False),
        Accion("ARCHIVOS", "Eliminar archivo",
               lambda: eliminar_elemento(arbol, auditoria, tabla_hash, "archivo"), True),
        Accion("ARCHIVOS", "Eliminar carpeta",
               lambda: eliminar_elemento(arbol, auditoria, tabla_hash, "carpeta"), True),
        Accion("ARCHIVOS", "Cambiar directorio",
               lambda: cambiar_directorio(arbol), False),
        Accion("ARCHIVOS", "Mostrar ruta actual",
               lambda: mostrar_ruta_actual(arbol), False),

        Accion("USUARIOS", "Registrar usuario",
               lambda: registrar_usuario(tabla_hash, auditoria), True),
        Accion("USUARIOS", "Eliminar usuario",
               lambda: eliminar_usuario(tabla_hash, auditoria), True),
        Accion("USUARIOS", "Mostrar usuario activo",
               lambda: mostrar_usuario_activo(tabla_hash), False),
        Accion("USUARIOS", "Mostrar tabla hash",
               lambda: mostrar_tabla_hash(tabla_hash), True),
        Accion("USUARIOS", "Demostrar colisiones",
               lambda: demostrar_colisiones(tabla_hash, auditoria), True),

        Accion("SISTEMA", "Ver auditoría",
               lambda: mostrar_auditoria(auditoria), True),
        Accion("SISTEMA", "Red y enrutamiento",
               red_y_enrutamiento, False),
    ]


def acciones_para_rol(acciones, es_administrador):
    """Filtra las acciones que puede ver y ejecutar el rol de la sesión."""
    if es_administrador:
        return list(acciones)
    return [accion for accion in acciones if not accion.solo_admin]


def preparar_administrador_inicial(tabla_hash, auditoria):
    """Crea la cuenta de administrador inicial si la tabla está vacía."""
    if len(tabla_hash) == 0:
        tabla_hash.registrarUsuario(
            ADMIN_INICIAL_USUARIO,
            ADMIN_INICIAL_CONTRASENA,
            "administrador"
        )
        auditoria.registrar(
            f"Sistema: administrador inicial '{ADMIN_INICIAL_USUARIO}' creado"
        )


def menu_sesion(tabla_hash, auditoria, acciones):
    """Menú de la sesión activa; termina al cerrar sesión."""
    while tabla_hash.haySesionActiva():
        disponibles = acciones_para_rol(acciones, tabla_hash.esAdministrador())
        mostrar_menu_rol(tabla_hash, disponibles)

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "0":
            cerrar_sesion(tabla_hash, auditoria)
            return

        if not opcion.isdigit() or not 1 <= int(opcion) <= len(disponibles):
            print("\n[ERROR] Opción inválida.")
            continue

        accion = disponibles[int(opcion) - 1]

        # Segunda barrera: aunque el menú ya oculta estas acciones al rol
        # 'usuario', se vuelve a comprobar el permiso antes de ejecutarlas.
        if accion.solo_admin and not tabla_hash.verificarPermiso(
                accion.descripcion.lower(),
                registrar_evento=auditoria.registrar):
            print(f"\n[ACCESO DENEGADO] {tabla_hash.ultimo_mensaje}")
            continue

        accion.ejecutar()


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main(archivo_auditoria="network_audit_log.txt",
         archivo_usuarios=None, archivo_red=None):
    """Si no se indican archivos de usuarios/red, todo vive solo en memoria
    (así los tests no tocan el disco). Abajo, el programa real pasa los reales."""
    auditoria = Auditoria(archivo_auditoria)
    arbol = ArbolDirectorios()
    tabla_hash = TablaHash(archivo=archivo_usuarios)
    red = GrafoServidores(archivo=archivo_red)

    # Si algún archivo de datos estaba dañado, queda constancia en la auditoría.
    for modulo in (tabla_hash, red):
        if modulo.ultimo_error:
            auditoria.registrar(f"Sistema: {modulo.ultimo_error}")

    preparar_administrador_inicial(tabla_hash, auditoria)
    acciones = definir_acciones(arbol, tabla_hash, auditoria, red)

    try:
        while True:
            mostrar_menu_inicio()

            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                if iniciar_sesion(tabla_hash, auditoria):
                    menu_sesion(tabla_hash, auditoria, acciones)

            elif opcion == "2":
                print("\nSaliendo del sistema...")
                break

            else:
                print("\n[ERROR] Opción inválida.")

    except (EOFError, KeyboardInterrupt):
        print("\n\nEntrada finalizada. Saliendo del sistema...")


if __name__ == "__main__":
    main(archivo_usuarios=ARCHIVO_USUARIOS, archivo_red=ARCHIVO_RED)