from datetime import datetime


class Auditoria:

    def __init__(self, archivo="network_audit_log.txt"):
        self.archivo = archivo

    def registrar(self, mensaje):
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.archivo, "a", encoding="utf-8") as archivo:
            archivo.write(f"[{fecha_hora}] {mensaje}\n")

    def mostrar_logs(self):
        try:
            with open(self.archivo, "r", encoding="utf-8") as archivo:
                contenido = archivo.read()

                if contenido:
                    print(contenido, end="")
                else:
                    print("No hay registros de auditoría.")

        except FileNotFoundError:
            print("No hay registros de auditoría.")