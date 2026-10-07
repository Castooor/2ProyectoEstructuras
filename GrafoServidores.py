from collections import deque


class GrafoServidores:
    """Grafo ponderado no dirigido. Vértices = servidores, aristas = latencia (ms)."""

    def __init__(self):
        # Lista de adyacencia: { "A": {"B": latencia, "C": latencia}, ... }
        self.servidores = {}

    # ------------------------------------------------------------------
    # Operaciones básicas
    # ------------------------------------------------------------------
    def agregar_servidor(self, servidor):
        """Agrega un servidor (vértice) a la red."""
        if servidor not in self.servidores:
            self.servidores[servidor] = {}

    def agregar_conexion(self, origen, destino, latencia):
        """Agrega una conexión bidireccional con peso = latencia."""
        if latencia < 0:
            raise ValueError("La latencia no puede ser negativa (Dijkstra no lo soporta).")
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

    def consultar_conexiones(self, servidor):
        """Devuelve {vecino: latencia} o None si el servidor no existe."""
        return self.servidores.get(servidor)

    def mostrar_red(self):
        """Imprime la estructura actual de la red."""
        print("--- Red de Servidores ---")
        if not self.servidores:
            print("La red está vacía.")
            return
        for servidor, conexiones in self.servidores.items():
            if not conexiones:
                print(f"Servidor {servidor}: Sin conexiones (Aislado)")
            else:
                conns = [f"{dest}({lat}ms)" for dest, lat in conexiones.items()]
                print(f"Servidor {servidor} conectado a: {', '.join(conns)}")
        print("-------------------------")

    # ------------------------------------------------------------------
    # Dijkstra (desde cero, O(V^2))
    # ------------------------------------------------------------------
    def dijkstra(self, origen, destino):
        """
        Ruta de menor latencia entre origen y destino.
        Devuelve (ruta, costo_total) o None si no existe ruta / servidores.
        No imprime: usar imprimir_ruta() para mostrar el resultado.
        """
        if origen not in self.servidores or destino not in self.servidores:
            return None

        if origen == destino:
            return [origen], 0

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

    def imprimir_ruta(self, origen, destino):
        """Ejecuta Dijkstra y muestra el resultado. Devuelve lo mismo que dijkstra()."""
        resultado = self.dijkstra(origen, destino)
        print("\n--- Simulación de Envío (Dijkstra) ---")
        if resultado is None:
            print(f"No hay ruta posible desde {origen} hasta {destino} "
                  f"(o alguno no existe en la red).")
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
            print(f"Costo total (Latencia): {costo} ms")
        print("--------------------------------------")
        return resultado

    # ------------------------------------------------------------------
    # Ping general (BFS)
    # ------------------------------------------------------------------
    def ping_general(self):
        """
        Diagnóstico con BFS. Devuelve un diccionario:
          {
            "conectada": bool,        # True si todos se comunican entre sí
            "componentes": [[...]],   # grupos de servidores conectados
            "aislados": [...]         # servidores sin ninguna conexión
          }
        No imprime: usar imprimir_diagnostico() para mostrarlo.
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

        aislados = [g[0] for g in componentes if len(g) == 1]
        return {
            "conectada": len(componentes) <= 1,
            "componentes": componentes,
            "aislados": aislados,
        }

    def imprimir_diagnostico(self):
        """Ejecuta el ping general y muestra el resultado."""
        print("\n--- Diagnóstico de Red (Ping General - BFS) ---")
        if not self.servidores:
            print("La red está vacía.")
            print("-----------------------------------------------")
            return None

        resultado = self.ping_general()
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
        return resultado