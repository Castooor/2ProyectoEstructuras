class GrafoServidores:
    def __init__(self):
        # Diccionario para representar el grafo (Lista de adyacencia)
        # Estructura: { "ServidorA": {"ServidorB": latencia, "ServidorC": latencia}, ... }
        self.servidores = {}

    def agregar_servidor(self, servidor):
        """Agrega un servidor (vértice) a la red."""
        if servidor not in self.servidores:
            self.servidores[servidor] = {}

    def agregar_conexion(self, origen, destino, latencia):
        """Agrega una conexión (arista) entre dos servidores con un peso (latencia)."""
        if origen not in self.servidores:
            self.agregar_servidor(origen)
        if destino not in self.servidores:
            self.agregar_servidor(destino)
        
        # Asumimos conexiones bidireccionales en la red
        self.servidores[origen][destino] = latencia
        self.servidores[destino][origen] = latencia

    def eliminar_conexion(self, origen, destino):
        """Elimina una conexión entre dos servidores."""
        if origen in self.servidores and destino in self.servidores[origen]:
            del self.servidores[origen][destino]
        if destino in self.servidores and origen in self.servidores[destino]:
            del self.servidores[destino][origen]

    def consultar_conexiones(self, servidor):
        """Devuelve un diccionario con las conexiones y latencias de un servidor."""
        if servidor in self.servidores:
            return self.servidores[servidor]
        return None

    def mostrar_red(self):
        """Muestra la estructura actual de la red de servidores."""
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

    def dijkstra(self, origen, destino):
        """
        Implementa el algoritmo de Dijkstra desde cero.
        Encuentra la ruta de menor costo (latencia) entre un servidor origen y un destino.
        """
        if origen not in self.servidores or destino not in self.servidores:
            print("El origen o destino no existen en la red.")
            return None

        # Inicialización
        distancias = {nodo: float('infinity') for nodo in self.servidores}
        predecesores = {nodo: None for nodo in self.servidores}
        distancias[origen] = 0
        nodos_no_visitados = list(self.servidores.keys())

        while nodos_no_visitados:
            # Seleccionar el nodo de menor costo de los no visitados
            nodo_actual = None
            menor_distancia = float('infinity')
            for nodo in nodos_no_visitados:
                if distancias[nodo] < menor_distancia:
                    menor_distancia = distancias[nodo]
                    nodo_actual = nodo

            # Si no hay nodo actual alcanzable, o ya llegamos al destino, terminamos
            if nodo_actual is None or menor_distancia == float('infinity'):
                break 
            
            if nodo_actual == destino:
                break
            
            nodos_no_visitados.remove(nodo_actual)

            # Actualizar distancias de los vecinos
            for vecino, latencia in self.servidores[nodo_actual].items():
                if vecino in nodos_no_visitados:
                    nueva_distancia = distancias[nodo_actual] + latencia
                    if nueva_distancia < distancias[vecino]:
                        distancias[vecino] = nueva_distancia
                        predecesores[vecino] = nodo_actual

        # Reconstruir la ruta origen → destino
        ruta = []
        nodo_paso = destino
        while nodo_paso is not None:
            ruta.insert(0, nodo_paso)
            nodo_paso = predecesores[nodo_paso]

        if distancias[destino] == float('infinity'):
            print(f"No hay ruta posible desde {origen} hasta {destino}")
            return None

        # Mostrar resultados según requerimientos
        costo_total = distancias[destino]
        saltos_intermedios = ruta[1:-1]
        
        print("\n--- Simulación de Envío (Dijkstra) ---")
        print(f"Origen: {origen}")
        print(f"Destino: {destino}")
        print(f"Saltos intermedios: {' -> '.join(saltos_intermedios) if saltos_intermedios else 'Ninguno (Conexión directa)'}")
        print(f"Ruta completa: {' -> '.join(ruta)}")
        print(f"Costo total (Latencia): {costo_total} ms")
        print("--------------------------------------")
        return ruta, costo_total

    def ping_general(self):
        """
        Implementa BFS para diagnosticar la red.
        Determina si todos los servidores están comunicados o detecta aislados.
        """
        if not self.servidores:
            print("La red está vacía.")
            return

        visitados = set()
        aislados = []
        componentes_conexos = 0

        print("\n--- Diagnóstico de Red (Ping General - BFS) ---")
        
        for servidor in self.servidores:
            if servidor not in visitados:
                componentes_conexos += 1
                
                # Implementación de BFS
                cola = [servidor]
                visitados_en_bfs = set([servidor])
                
                while cola:
                    actual = cola.pop(0)
                    visitados.add(actual)
                    
                    for vecino in self.servidores[actual]:
                        if vecino not in visitados_en_bfs:
                            visitados_en_bfs.add(vecino)
                            cola.append(vecino)
                
                # Si el BFS originado en este servidor no logró alcanzar ningún otro, está aislado
                if len(visitados_en_bfs) == 1:
                    aislados.append(servidor)

        if componentes_conexos == 1:
            print("Estado: Todos los servidores están comunicados entre sí.")
        else:
            print(f"Estado: La red está fragmentada. No todos los servidores se pueden comunicar.")
        
        if aislados:
            print(f"Servidores AISLADOS detectados: {', '.join(aislados)}")
        else:
            print("Servidores aislados: Ninguno.")
        print("-----------------------------------------------")


if __name__ == "__main__":
    print("===========================================")
    print("           PRUEBAS DEL MÓDULO              ")
    print("===========================================")

    # -----------------------------------------
    # Prueba 1: Dijkstra
    # -----------------------------------------
    print("\n=== PRUEBA 1: DIJKSTRA ===")
    print("Construyendo red:")
    print("A ----5---- B")
    print("|           |")
    print("2           3")
    print("|           |")
    print("C ----1---- D")
    
    red_dijkstra = GrafoServidores()
    red_dijkstra.agregar_conexion("A", "B", 5)
    red_dijkstra.agregar_conexion("A", "C", 2)
    red_dijkstra.agregar_conexion("B", "D", 3)
    red_dijkstra.agregar_conexion("C", "D", 1)
    
    red_dijkstra.mostrar_red()
    
    # Probar ruta A -> D
    print("\nBuscando ruta óptima de A hacia D...")
    red_dijkstra.dijkstra("A", "D")

    # -----------------------------------------
    # Prueba 2: BFS - Detección de aislados
    # -----------------------------------------
    print("\n=== PRUEBA 2: PING GENERAL (AISLADOS) ===")
    print("Construyendo red:")
    print("A — B — C")
    print("D (Aislado)")
    
    red_aislados = GrafoServidores()
    red_aislados.agregar_conexion("A", "B", 1)
    red_aislados.agregar_conexion("B", "C", 1)
    red_aislados.agregar_servidor("D") # Servidor D sin conexiones
    
    red_aislados.mostrar_red()
    
    print("\nEjecutando Ping General...")
    red_aislados.ping_general()
