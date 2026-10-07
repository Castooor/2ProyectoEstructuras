from GrafoServidores import GrafoServidores


def test_dijkstra_ruta_optima():
    #  A ----5---- B
    #  |           |
    #  2           3
    #  |           |
    #  C ----1---- D
    red = GrafoServidores()
    red.agregar_conexion("A", "B", 5)
    red.agregar_conexion("A", "C", 2)
    red.agregar_conexion("B", "D", 3)
    red.agregar_conexion("C", "D", 1)

    assert red.dijkstra("A", "D") == (["A", "C", "D"], 3)
    assert red.dijkstra("D", "A") == (["D", "C", "A"], 3)  # bidireccional
    assert red.dijkstra("A", "B") == (["A", "B"], 5)       # conexión directa


def test_dijkstra_origen_igual_destino():
    red = GrafoServidores()
    red.agregar_conexion("A", "B", 4)
    assert red.dijkstra("A", "A") == (["A"], 0)


def test_dijkstra_sin_ruta_o_inexistente():
    red = GrafoServidores()
    red.agregar_conexion("A", "B", 1)
    red.agregar_servidor("Z")
    assert red.dijkstra("A", "Z") is None   # existe pero no hay camino
    assert red.dijkstra("A", "X") is None   # destino no existe
    assert red.dijkstra("X", "A") is None   # origen no existe


def test_dijkstra_prefiere_camino_mas_largo_en_saltos_pero_barato():
    red = GrafoServidores()
    red.agregar_conexion("A", "D", 10)      # directo pero caro
    red.agregar_conexion("A", "B", 1)
    red.agregar_conexion("B", "C", 1)
    red.agregar_conexion("C", "D", 1)
    assert red.dijkstra("A", "D") == (["A", "B", "C", "D"], 3)


def test_eliminar_conexion_cambia_ruta():
    red = GrafoServidores()
    red.agregar_conexion("A", "B", 5)
    red.agregar_conexion("A", "C", 2)
    red.agregar_conexion("C", "B", 1)
    assert red.dijkstra("A", "B") == (["A", "C", "B"], 3)
    red.eliminar_conexion("C", "B")
    assert red.dijkstra("A", "B") == (["A", "B"], 5)
    assert "B" not in red.consultar_conexiones("C")


def test_latencia_negativa_rechazada():
    red = GrafoServidores()
    try:
        red.agregar_conexion("A", "B", -1)
        assert False, "Debió lanzar ValueError"
    except ValueError:
        pass


def test_ping_general_con_aislado():
    # A — B — C     D (aislado)
    red = GrafoServidores()
    red.agregar_conexion("A", "B", 1)
    red.agregar_conexion("B", "C", 1)
    red.agregar_servidor("D")

    r = red.ping_general()
    assert r["conectada"] is False
    assert r["aislados"] == ["D"]
    assert sorted(map(sorted, r["componentes"])) == [["A", "B", "C"], ["D"]]


def test_ping_general_red_conectada():
    red = GrafoServidores()
    red.agregar_conexion("A", "B", 1)
    red.agregar_conexion("B", "C", 1)
    r = red.ping_general()
    assert r["conectada"] is True
    assert r["aislados"] == []


def test_ping_general_dos_grupos_sin_aislados():
    red = GrafoServidores()
    red.agregar_conexion("A", "B", 1)
    red.agregar_conexion("C", "D", 1)
    r = red.ping_general()
    assert r["conectada"] is False
    assert r["aislados"] == []


if __name__ == "__main__":
    # Ejecuta todas las pruebas sin necesitar pytest
    pruebas = [f for n, f in list(globals().items()) if n.startswith("test_")]
    for prueba in pruebas:
        prueba()
        print(f"OK  {prueba.__name__}")
    print(f"\n{len(pruebas)} pruebas pasaron.")

    # Demostración visual (para mostrar en la defensa)
    print("\n=== DEMO: DIJKSTRA ===")
    demo = GrafoServidores()
    demo.agregar_conexion("A", "B", 5)
    demo.agregar_conexion("A", "C", 2)
    demo.agregar_conexion("B", "D", 3)
    demo.agregar_conexion("C", "D", 1)
    demo.mostrar_red()
    demo.imprimir_ruta("A", "D")

    print("\n=== DEMO: PING GENERAL ===")
    demo2 = GrafoServidores()
    demo2.agregar_conexion("A", "B", 1)
    demo2.agregar_conexion("B", "C", 1)
    demo2.agregar_servidor("D")
    demo2.mostrar_red()
    demo2.imprimir_diagnostico()