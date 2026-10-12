"""
Submenú de consola del módulo Grafos y Enrutamiento (Brayan).

NO es el menú principal del sistema: Allison lo llama desde su menú con
    menu_grafos(red, registrar=auditoria.registrar)
"""
import math

from GrafoServidores import GrafoServidores


def _pedir_texto(mensaje):
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("  El valor no puede estar vacío.")


def _pedir_latencia(mensaje):
    while True:
        try:
            valor = float(input(mensaje).strip())
        except ValueError:
            print("  Ingresa un número válido.")
            continue
        if not math.isfinite(valor):
            print("  Ingresa un número válido.")
            continue
        if valor < 0:
            print("  La latencia no puede ser negativa.")
            continue
        return int(valor) if valor.is_integer() else valor


def menu_grafos(red, registrar=None, solo_lectura=False):
    """
    red:         la instancia ÚNICA de GrafoServidores del sistema.
    registrar:   función opcional registrar(texto) para la auditoría.
                 Si es None, no se registra nada.
    solo_lectura: si es True (rol "usuario") solo se pueden consultar la red,
                 calcular rutas y hacer ping; agregar servidores y crear o
                 eliminar conexiones (opciones 1, 2 y 3) quedan bloqueadas.
    """
    def log(texto):
        if registrar:
            registrar(texto)

    def guardar_red():
        """Guarda la red; si falla avisa en pantalla y lo deja en la auditoría."""
        if not red.guardar():
            print(f"  ADVERTENCIA: {red.ultimo_error}")
            log(f"ERROR de persistencia: {red.ultimo_error}")

    while True:
        print("\n========== RED Y ENRUTAMIENTO ==========")
        if solo_lectura:
            print("(Modo consulta: su rol no permite modificar la red)")
        else:
            print("1. Agregar servidor")
            print("2. Agregar conexión")
            print("3. Eliminar conexión")
        print("4. Consultar conexiones de un servidor")
        print("5. Mostrar la red")
        print("6. Simular envío de paquete (Dijkstra)")
        print("7. Ping general (BFS)")
        if not solo_lectura:
            print("8. Modificar latencia de una conexión")
            print("9. Renombrar servidor")
            print("10. Eliminar servidor")
        print("0. Volver")
        opcion = input("Seleccione una opción: ").strip()

        if solo_lectura and opcion in ("1", "2", "3", "8", "9", "10"):
            print("Acción no permitida para su rol.")

        elif opcion == "1":
            s = _pedir_texto("Nombre del servidor: ")
            if s in red.servidores:
                print(f"El servidor {s} ya existe.")
            else:
                red.agregar_servidor(s)
                print(f"Servidor {s} agregado.")
                log(f"Se agregó el servidor {s}")
                guardar_red()

        elif opcion == "2":
            a = _pedir_texto("Servidor origen: ")
            b = _pedir_texto("Servidor destino: ")
            if a == b:
                print("Un servidor no puede conectarse consigo mismo.")
                continue
            lat = _pedir_latencia("Latencia (ms): ")
            red.agregar_conexion(a, b, lat)
            print(f"Conexión {a} <-> {b} ({lat} ms) creada.")
            log(f"Se creó la conexión {a}-{b} con latencia {lat} ms")
            guardar_red()

        elif opcion == "3":
            a = _pedir_texto("Servidor origen: ")
            b = _pedir_texto("Servidor destino: ")
            conexiones = red.consultar_conexiones(a)
            if conexiones is None or b not in conexiones:
                print("Esa conexión no existe.")
            else:
                red.eliminar_conexion(a, b)
                print(f"Conexión {a} <-> {b} eliminada.")
                log(f"Se eliminó la conexión {a}-{b}")
                guardar_red()

        elif opcion == "4":
            s = _pedir_texto("Servidor: ")
            conexiones = red.consultar_conexiones(s)
            if conexiones is None:
                print(f"El servidor {s} no existe.")
            elif not conexiones:
                print(f"El servidor {s} no tiene conexiones (aislado).")
            else:
                for vecino, lat in conexiones.items():
                    print(f"  {s} -> {vecino}: {lat} ms")

        elif opcion == "5":
            red.mostrar_red()

        elif opcion == "6":
            a = _pedir_texto("Servidor origen: ")
            b = _pedir_texto("Servidor destino: ")
            resultado = red.dijkstra(a, b)
            if resultado:
                ruta, costo = resultado
                log(f"Se calculó la ruta {' -> '.join(ruta)} con costo {costo} ms")
            else:
                log(f"Ruta {a}-{b}: sin ruta posible")

        elif opcion == "7":
            diag = red.ping_general()
            estado = "red conectada" if diag["conectada"] else "red fragmentada"
            aislados = ", ".join(diag["aislados"]) or "ninguno"
            log(f"Ping general: {estado}; aislados: {aislados}")

        elif opcion == "8":
            a = _pedir_texto("Servidor origen: ")
            b = _pedir_texto("Servidor destino: ")
            conexiones = red.consultar_conexiones(a)
            if conexiones is None or b not in conexiones:
                print("Esa conexión no existe.")
                continue
            anterior = conexiones[b]
            lat = _pedir_latencia(f"Nueva latencia (actual {anterior} ms): ")
            red.modificar_latencia(a, b, lat)
            print(f"Conexión {a} <-> {b} ahora tiene {lat} ms.")
            log(f"Se modificó la latencia de {a}-{b}: {anterior} ms -> {lat} ms")
            guardar_red()

        elif opcion == "9":
            viejo = _pedir_texto("Servidor a renombrar: ")
            if viejo not in red.servidores:
                print(f"El servidor {viejo} no existe.")
                continue
            nuevo = _pedir_texto("Nuevo nombre: ")
            if red.renombrar_servidor(viejo, nuevo):
                print(f"Servidor {viejo} renombrado a {nuevo}.")
                log(f"Se renombró el servidor {viejo} a {nuevo}")
                guardar_red()
            else:
                print(f"El nombre {nuevo} ya está en uso.")

        elif opcion == "10":
            s = _pedir_texto("Servidor a eliminar: ")
            conexiones = red.consultar_conexiones(s)
            if conexiones is None:
                print(f"El servidor {s} no existe.")
                continue
            confirmar = input(
                f"¿Eliminar {s} y sus {len(conexiones)} conexión(es)? (s/n): "
            ).strip().lower()
            if confirmar != "s":
                print("Operación cancelada.")
                continue
            red.eliminar_servidor(s)
            print(f"Servidor {s} eliminado.")
            log(f"Se eliminó el servidor {s} y sus conexiones")
            guardar_red()

        elif opcion == "0":
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    # Solo para probar tu submenú por separado
    menu_grafos(GrafoServidores(), registrar=lambda t: print(f"  [LOG] {t}"))