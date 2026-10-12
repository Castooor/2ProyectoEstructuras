import json
import math
import os
from collections import deque


class GrafoServidores:
    """Grafo ponderado no dirigido. Vértices = servidores, aristas = latencia (ms)."""

    def __init__(self, archivo=None):
        # Lista de adyacencia: { "A": {"B": latencia, "C": latencia}, ... }
        self.servidores = {}
        # Persistencia: si se indica un archivo JSON, la red se carga al crear
        # el grafo; para guardarla se llama a guardar() tras cada cambio.
        self.archivo = archivo
        self.ultimo_error = ""      # ultimo problema de persistencia ("" si no hubo)
        if self.archivo:
            self.cargar()

    # ------------------------------------------------------------------
    # Persistencia (archivo JSON)
    # ------------------------------------------------------------------
    def guardar(self):
        """Guarda la red completa en el archivo JSON (si hay archivo).

        Nunca lanza excepciones: devuelve True si guardó (o si no hay archivo)
        y False si falló; en ese caso el motivo queda en 'ultimo_error'.
        """
        if not self.archivo:
            return True
        temporal = self.archivo + ".tmp"
        try:
            with open(temporal, "w", encoding="utf-8") as f:
                json.dump({"servidores": self.servidores}, f, ensure_ascii=False,
                          indent=2, allow_nan=False)
            os.replace(temporal, self.archivo)
        except (OSError, ValueError, TypeError) as error:
            self.ultimo_error = f"No se pudo guardar '{self.archivo}': {error}"
            try:
                os.remove(temporal)
            except OSError:
                pass
            return False
        self.ultimo_error = ""
        return True

    def cargar(self):
        """Reconstruye la red desde el archivo JSON.

        Si el archivo no existe no hace nada. Si está dañado lo respalda como
        '<archivo>.corrupto', deja la red vacía y el motivo en 'ultimo_error'.
        Nunca lanza excepciones. Devuelve True si cargó datos.
        """
        if not self.archivo or not os.path.exists(self.archivo):
            return False
        try:
            with open(self.archivo, "r", encoding="utf-8") as f:
                datos = json.load(f)
            nueva = {}
            for servidor, vecinos in datos["servidores"].items():
                nueva[servidor] = {}
                for vecino, latencia in vecinos.items():
                    if (isinstance(latencia, bool)
                            or not isinstance(latencia, (int, float))
                            or not math.isfinite(latencia) or latencia < 0):
                        raise ValueError("latencia invalida")
                    nueva[servidor][vecino] = latencia
            for servidor, vecinos in nueva.items():       # toda arista debe ser bidireccional
                for vecino, latencia in vecinos.items():
                    if vecino not in nueva or nueva[vecino].get(servidor) != latencia:
                        raise ValueError("red inconsistente")
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            self.servidores = {}
            try:
                os.replace(self.archivo, self.archivo + ".corrupto")
            except OSError:
                pass
            self.ultimo_error = (f"Archivo de red '{self.archivo}' dañado o ilegible; "
                                 "se respaldó como .corrupto y se inició vacía.")
            return False
        self.servidores = nueva
        return True

    # ------------------------------------------------------------------
    # Operaciones básicas
    # ------------------------------------------------------------------
    def agregar_servidor(self, servidor):
        """Agrega un servidor (vértice) a la red."""
        if servidor not in self.servidores:
            self.servidores[servidor] = {}

    def agregar_conexion(self, origen, destino, latencia):
        """Agrega una conexión bidireccional con peso = latencia."""
        if not math.isfinite(latencia) or latencia < 0:
            raise ValueError("La latencia debe ser un número finito y no negativo.")
        self.agregar_servidor(origen)
        self.agregar_servidor(destino)
        self.servidores[origen][destino] = latencia
        self.servidores[destino][origen] = latencia

    def eliminar_conexion(self, origen, destino):
        """Elimina la conexión entre dos servidores."""
        if origen in self.servidores:
            self.servidores[origen].pop(destino, None)
        if destino in self.servidores:
            self.servidores[destino].pop(origen, None)

    def modificar_latencia(self, origen, destino, nueva_latencia):
        """Cambia la latencia de una conexión existente (en ambos sentidos).

        Devuelve True si se modificó; False si la conexión no existe.
        """
        if not math.isfinite(nueva_latencia) or nueva_latencia < 0:
            raise ValueError("La latencia debe ser un número finito y no negativo.")
        if origen not in self.servidores or destino not in self.servidores[origen]:
            return False
        self.servidores[origen][destino] = nueva_latencia
        self.servidores[destino][origen] = nueva_latencia
        return True

    def renombrar_servidor(self, actual, nuevo):
        """Cambia el nombre de un servidor conservando todas sus conexiones.

        Devuelve True si se renombró; False si 'actual' no existe o 'nuevo'
        ya está en uso.
        """
        if actual not in self.servidores or nuevo in self.servidores:
            return False
        renombrada = {}
        for servidor, vecinos in self.servidores.items():
            clave = nuevo if servidor == actual else servidor
            renombrada[clave] = {(nuevo if v == actual else v): lat
                                 for v, lat in vecinos.items()}
        self.servidores = renombrada
        return True

    def eliminar_servidor(self, servidor):
        """Elimina un servidor y todas las conexiones que llegan a él.

        Devuelve True si existía y se eliminó; False si no existe.
        """
        if servidor not in self.servidores:
            return False
        for vecino in self.servidores[servidor]:
            self.servidores[vecino].pop(servidor, None)
        del self.servidores[servidor]
        return True

    def consultar_conexiones(self, servidor):
        """Devuelve {vecino: latencia} o None si el servidor no existe."""
        return self.servidores.get(servidor)

    def mostrar_red(self):
        """Imprime la estructura actual de la red."""
        print("--- Red de Servidores ---")
        if not self.servidores:
            print("La red está vacía.")
            return None
        for servidor, conexiones in self.servidores.items():
            if not conexiones:
                print(f"Servidor {servidor}: Sin conexiones (Aislado)")
            else:
                conns = [f"{dest}({lat}ms)" for dest, lat in conexiones.items()]
                print(f"Servidor {servidor} conectado a: {', '.join(conns)}")
        print("-------------------------")
        return None

    # ------------------------------------------------------------------
    # Dijkstra (desde cero, O(V^2))
    # ------------------------------------------------------------------
    def dijkstra(self, origen, destino, mostrar=True):
        """
        Ruta de menor latencia entre origen y destino.
        Imprime el resultado en consola (si mostrar=True) y devuelve
        (ruta, costo_total), o None si no hay ruta o algún servidor no existe.
        """
        if origen not in self.servidores or destino not in self.servidores:
            if mostrar:
                print("El origen o destino no existen en la red.")
            return None

        if origen == destino:
            resultado = ([origen], 0)
        else:
            resultado = self._calcular_ruta(origen, destino)

        if mostrar:
            self._imprimir_ruta(origen, destino, resultado)
        return resultado

    def _calcular_ruta(self, origen, destino):
        distancias = {nodo: float("inf") for nodo in self.servidores}
        predecesores = {nodo: None for nodo in self.servidores}
        distancias[origen] = 0
        no_visitados = set(self.servidores)

        while no_visitados:
            # Nodo no visitado con menor distancia acumulada
            actual = None
            menor = float("inf")
            for nodo in no_visitados:
                if distancias[nodo] < menor:
                    menor = distancias[nodo]
                    actual = nodo

            # Los que quedan son inalcanzables, o ya llegamos al destino
            if actual is None or actual == destino:
                break

            no_visitados.remove(actual)

            # Relajación de aristas
            for vecino, latencia in self.servidores[actual].items():
                if vecino in no_visitados:
                    nueva = distancias[actual] + latencia
                    if nueva < distancias[vecino]:
                        distancias[vecino] = nueva
                        predecesores[vecino] = actual

        if distancias[destino] == float("inf"):
            return None

        # Reconstrucción de la ruta destino -> origen, luego se invierte
        ruta = []
        paso = destino
        while paso is not None:
            ruta.append(paso)
            paso = predecesores[paso]
        ruta.reverse()
        return ruta, distancias[destino]

    def _imprimir_ruta(self, origen, destino, resultado):
        print("\n--- Simulación de Envío (Dijkstra) ---")
        if resultado is None:
            print(f"No hay ruta posible desde {origen} hasta {destino}")
        else:
            ruta, costo = resultado
            intermedios = ruta[1:-1]
            print(f"Origen: {origen}")
            print(f"Destino: {destino}")
            if origen == destino:
                print("Origen y destino son el mismo servidor.")
            else:
                print("Saltos intermedios: "
                      f"{' -> '.join(intermedios) if intermedios else 'Ninguno (Conexión directa)'}")
            print(f"Ruta completa: {' -> '.join(ruta)}")
            if len(ruta) > 1:
                print("Detalle de saltos:")
                for i in range(len(ruta) - 1):
                    a, b = ruta[i], ruta[i + 1]
                    print(f"  Salto {i + 1}: {a} -> {b} ({self.servidores[a][b]} ms)")
            print(f"Costo total (Latencia): {costo} ms")
        print("--------------------------------------")

    # ------------------------------------------------------------------
    # Ping general (BFS)
    # ------------------------------------------------------------------
    def ping_general(self, mostrar=True):
        """
        Diagnóstico de la red con BFS. Imprime en consola (si mostrar=True)
        y devuelve un diccionario:
          {"conectada": bool, "componentes": [[...]], "aislados": [...]}
        """
        visitados = set()
        componentes = []

        for servidor in self.servidores:
            if servidor in visitados:
                continue
            grupo = []
            cola = deque([servidor])
            visitados.add(servidor)
            while cola:
                actual = cola.popleft()
                grupo.append(actual)
                for vecino in self.servidores[actual]:
                    if vecino not in visitados:
                        visitados.add(vecino)
                        cola.append(vecino)
            componentes.append(grupo)

        resultado = {
            "conectada": len(componentes) <= 1,
            "componentes": componentes,
            "aislados": [g[0] for g in componentes if len(g) == 1],
        }

        if mostrar:
            self._imprimir_diagnostico(resultado)
        return resultado

    def _imprimir_diagnostico(self, resultado):
        print("\n--- Diagnóstico de Red (Ping General - BFS) ---")
        if not self.servidores:
            print("La red está vacía.")
        else:
            if resultado["conectada"]:
                print("Estado: Todos los servidores están comunicados entre sí.")
            else:
                print("Estado: La red está fragmentada. No todos los servidores se pueden comunicar.")
                for i, grupo in enumerate(resultado["componentes"], start=1):
                    print(f"  Grupo {i}: {', '.join(grupo)}")
            if resultado["aislados"]:
                print(f"Servidores AISLADOS detectados: {', '.join(resultado['aislados'])}")
            else:
                print("Servidores aislados: Ninguno.")
        print("-----------------------------------------------")