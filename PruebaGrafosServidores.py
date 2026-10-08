from GrafoServidores import GrafoServidores


def test_dijkstra_ruta_optima():
    red = GrafoServidores()
    red.agregar_conexion("A", "B", 5)
    red.agregar_conexion("A", "C", 2)
    red.agregar_conexion("B", "D", 3)
    red.agregar_conexion("C", "D", 1)

    assert red.dijkstra("A", "D", mostrar=False) == (["A", "C", "D"], 3)
    assert red.dijkstra("D", "A", mostrar=False) == (["D", "C", "A"], 3)
    assert red.dijkstra("A", "B", mostrar=False) == (["A", "B"], 5)


def test_dijkstra_origen_igual_destino():
    red = GrafoServidores()
    red.agregar_conexion("A", "B", 4)
    assert red.dijkstra("A", "A", mostrar=False) == (["A"], 0)


def test_dijkstra_sin_ruta_o_inexistente():
    red = GrafoServidores()
    red.agregar_conexion("A", "B", 1)
    red.agregar_servidor("Z")
    assert red.dijkstra("A", "Z", mostrar=False) is None
    assert red.dijkstra("A", "X", mostrar=False) is None
    assert red.dijkstra("X", "A", mostrar=False) is None


def test_dijkstra_camino_directo_caro():
    red = GrafoServidores()
    red.agregar_conexion("A", "D", 10)
    red.agregar_conexion("A", "B", 1)
    red.agregar_conexion("B", "C", 1)
    red.agregar_conexion("C", "D", 1)
    assert red.dijkstra("A", "D", mostrar=False) == (["A", "B", "C", "D"], 3)


def test_eliminar_conexion_cambia_ruta():
    red = GrafoServidores()
    red.agregar_conexion("A", "B", 5)
    red.agregar_conexion("A", "C", 2)
    red.agregar_conexion("C", "B", 1)
    assert red.dijkstra("A", "B", mostrar=False) == (["A", "C", "B"], 3)
    red.eliminar_conexion("C", "B")
    assert red.dijkstra("A", "B", mostrar=False) == (["A", "B"], 5)
    assert "B" not in red.consultar_conexiones("C")


def test_latencia_negativa_rechazada():
    red = GrafoServidores()
    try:
        red.agregar_conexion("A", "B", -1)
        assert False, "Debió lanzar ValueError"
    except ValueError:
        pass


def test_ping_general_con_aislado():
    red = GrafoServidores()
    red.agregar_conexion("A", "B", 1)
    red.agregar_conexion("B", "C", 1)
    red.agregar_servidor("D")
    r = red.ping_general(mostrar=False)
    assert r["conectada"] is False
    assert r["aislados"] == ["D"]
    assert sorted(map(sorted, r["componentes"])) == [["A", "B", "C"], ["D"]]


def test_ping_general_red_conectada():
    red = GrafoServidores()
    red.agregar_conexion("A", "B", 1)
    red.agregar_conexion("B", "C", 1)
    r = red.ping_general(mostrar=False)
    assert r["conectada"] is True
    assert r["aislados"] == []


if __name__ == "__main__":
    pruebas = [f for n, f in list(globals().items()) if n.startswith("test_")]
    for prueba in pruebas:
        prueba()
        print(f"OK  {prueba.__name__}")
    print(f"\n{len(pruebas)} pruebas pasaron.")

    print("\n=== PRUEBA 1: DIJKSTRA ===")
    print("A ----5---- B\n|           |\n2           3\n|           |\nC ----1---- D")
    red1 = GrafoServidores()
    red1.agregar_conexion("A", "B", 5)
    red1.agregar_conexion("A", "C", 2)
    red1.agregar_conexion("B", "D", 3)
    red1.agregar_conexion("C", "D", 1)
    red1.mostrar_red()
    red1.dijkstra("A", "D")

    print("\n=== PRUEBA 2: PING GENERAL (AISLADOS) ===")
    print("A — B — C\nD (Aislado)")
    red2 = GrafoServidores()
    red2.agregar_conexion("A", "B", 1)
    red2.agregar_conexion("B", "C", 1)
    red2.agregar_servidor("D")
    red2.mostrar_red()
    red2.ping_general()