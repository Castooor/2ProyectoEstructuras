from ArbolDirectorios import ArbolDirectorios
from auditoria import Auditoria


def mostrar_menu():
    print("\n========================================")
    print(" SISTEMA DE ARCHIVOS DISTRIBUIDO")
    print("========================================")
    print("1. Crear carpeta")
    print("2. Crear archivo")
    print("3. Buscar archivo")
    print("4. Mostrar árbol")
    print("5. Eliminar archivo")
    print("6. Eliminar carpeta")
    print("7. Cambiar directorio")
    print("8. Mostrar ruta actual")
    print("9. Ver auditoría")
    print("0. Salir")
    print("========================================")


def crear_carpeta(arbol, auditoria):
    nombre = input("Nombre de la carpeta: ").strip()
    destino = input(
        "Ruta de destino (Enter para el directorio actual): "
    ).strip()

    if destino == "":
        destino = None

    resultado = arbol.crearCarpeta(
        nombre,
        destino=destino,
        registrar_evento=auditoria.registrar
    )

    if resultado is not None:
        print(f"\n[OK] {arbol.ultimo_mensaje}")
    else:
        print(f"\n[ERROR] {arbol.ultimo_mensaje}")


def crear_archivo(arbol, auditoria):
    nombre = input("Nombre del archivo: ").strip()

    destino = input(
        "Ruta de destino (Enter para el directorio actual): "
    ).strip()

    contenido = input("Contenido del archivo: ")

    if destino == "":
        destino = None

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


def buscar_archivo(arbol):
    nombre = input("Nombre del archivo a buscar: ").strip()

    resultado = arbol.buscarArchivo(nombre)

    if resultado is not None:
        print("\n[ENCONTRADO]")
        print(f"Nombre: {resultado.nombre}")
        print(f"Ruta: {resultado.obtenerRuta()}")
    else:
        print(f"\n[NO ENCONTRADO] {arbol.ultimo_mensaje}")


def mostrar_arbol(arbol):
    print("\n========== ÁRBOL DE DIRECTORIOS ==========")
    arbol.mostrarArbol(estilo="arbol")
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


def mostrar_auditoria(auditoria):
    print("\n========== AUDITORÍA ==========")
    auditoria.mostrar_logs()
    print("===============================")


def main():
    auditoria = Auditoria()
    arbol = ArbolDirectorios()

    print("========================================")
    print(" SISTEMA DE ARCHIVOS DISTRIBUIDO")
    print("========================================")
    print("\nSistema iniciado correctamente.")
    print("Arbol de directorios: OK")
    print("Auditoria: OK")

    while True:
        mostrar_menu()

        opcion = input("Seleccione una opción: ").strip()

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

        elif opcion == "9":
            mostrar_auditoria(auditoria)

        elif opcion == "0":
            print("\nSaliendo del sistema...")
            break

        else:
            print(
                "\n[ERROR] Opción inválida. "
                "Seleccione una opción del 0 al 9."
            )


if __name__ == "__main__":
    main()