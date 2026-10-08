# -*- coding: utf-8 -*-
"""
Punto de entrada para probar manualmente la tabla hash de usuarios.

Uso:
    cd Proyecto#2Datos
    python main.py

Permite registrar usuarios, iniciar sesion, buscar, validar credenciales,
eliminar usuarios, inspeccionar las cadenas (colisiones) de cada indice, ver
la funcion hash de un nombre y consultar las estadisticas de la tabla.

Las pruebas automaticas, sin interaccion, siguen disponibles con:
    python TablaHash.py
"""

from TablaHash import TablaHash

# Eventos de auditoria que la tabla envia a traves del callback.
EVENTOS_AUDITORIA = []


def registrarEvento(mensaje):
    """Callback de auditoria que se pasa a los metodos de la tabla.

    Aqui es donde el sistema completo podria hacer el 'append' al archivo
    network_audit_log.txt; en este main los eventos solo se muestran.
    """
    EVENTOS_AUDITORIA.append(mensaje)
    print("      [AUDITORIA] %s" % mensaje)


def pedir(texto):
    """Lee una linea de la consola sin espacios sobrantes."""
    return input(texto).strip()


def pausar():
    """Detiene la pantalla hasta que la persona presione ENTER."""
    input("\n  Presione ENTER para continuar...")


def pedirNombre():
    """Pide un nombre de usuario. Devuelve None si se deja vacio."""
    nombre = pedir("  Nombre de usuario: ")
    if nombre == "":
        print("  [AVISO] Debe escribir un nombre de usuario.")
        return None
    return nombre


def opcionRegistrar(tabla):
    """Registra un usuario nuevo en la tabla hash."""
    print("\n--- REGISTRAR USUARIO ---")
    nombre = pedirNombre()
    if nombre is None:
        return
    contrasena = input("  Contrasena: ")
    rol = pedir("  Rol (usuario/administrador) [usuario]: ") or "usuario"
    if tabla.registrarUsuario(nombre, contrasena, rol, registrar_evento=registrarEvento):
        print("  [OK]    %s" % tabla.ultimo_mensaje)
    else:
        print("  [AVISO] %s" % tabla.ultimo_mensaje)


def opcionIniciarSesion(tabla):
    """Valida credenciales y abre la sesion del usuario."""
    print("\n--- INICIAR SESION ---")
    nombre = pedirNombre()
    if nombre is None:
        return
    contrasena = input("  Contrasena: ")
    if tabla.iniciarSesion(nombre, contrasena, registrar_evento=registrarEvento):
        activo = tabla.usuarioActivo
        print("  [OK] Bienvenido, %s (rol %s)." % (activo.nombre, activo.rol))
    else:
        print("  [DENEGADO] %s" % tabla.ultimo_mensaje)


def opcionBuscar(tabla):
    """Busca un usuario y muestra el indice donde quedo almacenado."""
    print("\n--- BUSCAR USUARIO ---")
    nombre = pedirNombre()
    if nombre is None:
        return
    nodo = tabla.buscarUsuario(nombre)
    if nodo is None:
        print("  El usuario '%s' NO existe en la tabla." % nombre)
    else:
        print("  Encontrado: %s | rol: %s | indice: %d" %
              (nodo.nombre, nodo.rol, tabla.funcionHash(nodo.nombre)))


def opcionValidar(tabla):
    """Valida usuario y contrasena sin abrir sesion."""
    print("\n--- VALIDAR CREDENCIALES ---")
    nombre = pedirNombre()
    if nombre is None:
        return
    contrasena = input("  Contrasena: ")
    if tabla.validarCredenciales(nombre, contrasena):
        print("  [VALIDA]   Usuario y contrasena correctos.")
    else:
        print("  [INVALIDA] Usuario o contrasena incorrectos (no se indica cual).")


def opcionEliminar(tabla):
    """Elimina un usuario reconectando los enlaces de su cadena."""
    print("\n--- ELIMINAR USUARIO ---")
    nombre = pedirNombre()
    if nombre is None:
        return
    if tabla.eliminarUsuario(nombre, registrar_evento=registrarEvento):
        print("  [OK]    %s" % tabla.ultimo_mensaje)
    else:
        print("  [AVISO] %s" % tabla.ultimo_mensaje)


def opcionMostrarTabla(tabla):
    """Muestra la tabla completa y permite inspeccionar una cadena concreta."""
    print()
    tabla.mostrarTabla()
    texto = pedir("\n  Ver la cadena de un indice? (numero o ENTER para omitir): ")
    if texto == "":
        return
    try:
        indice = int(texto)
    except ValueError:
        print("  [AVISO] '%s' no es un numero de indice." % texto)
        return
    try:
        nombres = tabla.obtenerCadena(indice)
    except IndexError as error:
        print("  [ERROR] %s" % error)
        return
    if not nombres:
        print("  Indice %d: cadena vacia (nadie colisiona ahi)." % indice)
    else:
        print("  Indice %d: %s" % (indice, " -> ".join(nombres)))


def opcionEstadisticas(tabla):
    """Muestra ocupacion, colisiones y factor de carga de la tabla."""
    print("\n--- ESTADISTICAS DE LA TABLA ---")
    for clave, valor in tabla.estadisticas().items():
        print("  %-20s %s" % (clave, valor))


def opcionFuncionHash(tabla):
    """Muestra el calculo de la funcion hash para un nombre."""
    print("\n--- FUNCION HASH (nombre -> codigo -> indice) ---")
    nombre = pedirNombre()
    if nombre is None:
        return
    print("  codigoHash(nombre)  = %d" % tabla.codigoHash(nombre))
    print("  funcionHash(nombre) = %d      es codigoHash %% %d" %
          (tabla.funcionHash(nombre), tabla.tamano))


def opcionCerrarSesion(tabla):
    """Cierra la sesion activa, si existe."""
    print("\n--- CERRAR SESION ---")
    nombre = tabla.cerrarSesion(registrar_evento=registrarEvento)
    if nombre is None:
        print("  No hay ninguna sesion activa.")
    else:
        print("  [OK] Sesion cerrada: %s" % nombre)

def opcionProbarPermiso(tabla):
    """Comprueba si la sesion activa puede ejecutar una accion de administrador."""
    print("\n--- PROBAR PERMISO DE ADMINISTRADOR ---")
    accion = pedir("  Accion a probar [eliminar carpeta]: ") or "eliminar carpeta"
    if tabla.usuarioActivo is None:
        print("  [DENEGADO] No hay sesion activa.")
        return
    if tabla.verificarPermiso(accion, registrar_evento=registrarEvento):
        print("  [PERMITIDO] La sesion activa es administrador.")
    else:
        print("  [DENEGADO]  %s" % tabla.ultimo_mensaje)



def opcionCargarUsuariosDePrueba(tabla):
    """Carga los cuatro usuarios de prueba del equipo."""
    print("\n--- CARGAR USUARIOS DE PRUEBA ---")
    usuarios = [
        ("santiago", "Santi2026", "administrador"),
        ("brayan", "Brayan123", "usuario"),
        ("kenan", "Kenan123", "administrador"),
        ("allison", "Allison123", "usuario"),
    ]
    for nombre, contrasena, rol in usuarios:
        tabla.registrarUsuario(nombre, contrasena, rol, registrar_evento=registrarEvento)
        print("  %-9s -> indice %2d | %s" %
              (nombre, tabla.funcionHash(nombre), tabla.ultimo_mensaje))


MENU = [
    ("1", "Registrar usuario", opcionRegistrar),
    ("2", "Iniciar sesion", opcionIniciarSesion),
    ("3", "Buscar usuario", opcionBuscar),
    ("4", "Validar credenciales", opcionValidar),
    ("5", "Eliminar usuario", opcionEliminar),
    ("6", "Mostrar tabla hash completa", opcionMostrarTabla),
    ("7", "Ver la funcion hash de un nombre", opcionFuncionHash),
    ("8", "Ver estadisticas", opcionEstadisticas),
    ("9", "Cerrar sesion activa", opcionCerrarSesion),
    ("10", "Cargar los 4 usuarios de prueba", opcionCargarUsuariosDePrueba),
    ("11", "Probar permiso de administrador", opcionProbarPermiso),
    ("0", "Salir", None),
]


def mostrarMenu(tabla):
    """Dibuja el menu con el estado actual de la tabla y de la sesion."""
    activo = tabla.usuarioActivo
    print("\n" + "=" * 58)
    print(" TABLA HASH DE USUARIOS - PRUEBAS MANUALES")
    print("=" * 58)
    print(" Tamano: %d indices | usuarios: %d | sesion: %s" %
          (tabla.tamano, len(tabla), activo.nombre if activo else "(ninguna)"))
    print("-" * 58)
    for numero, descripcion, _ in MENU:
        print("  %2s. %s" % (numero, descripcion))
    print("-" * 58)


def main():
    """Crea la tabla de 50 indices y ejecuta el bucle del menu."""
    tabla = TablaHash()
    acciones = dict((numero, accion) for numero, _, accion in MENU if accion)
    print("Bienvenido. Tabla hash creada con %d indices." % tabla.tamano)

    while True:
        mostrarMenu(tabla)
        try:
            opcion = pedir("Seleccione una opcion: ")
        except (EOFError, KeyboardInterrupt):
            print("\nEntrada finalizada. Saliendo...")
            break

        if opcion == "0":
            print("\nSaliendo. Eventos de auditoria generados: %d" % len(EVENTOS_AUDITORIA))
            break

        accion = acciones.get(opcion)
        if accion is None:
            print("  [AVISO] Opcion invalida: '%s'." % opcion)
            continue

        try:
            accion(tabla)
        except ValueError as error:              # por ejemplo, campos vacios
            print("  [ERROR] %s" % error)
        except (EOFError, KeyboardInterrupt):
            print("\nEntrada finalizada. Saliendo...")
            break

        try:
            pausar()
        except (EOFError, KeyboardInterrupt):
            print("\nEntrada finalizada. Saliendo...")
            break


if __name__ == "__main__":
    main()
