# -*- coding: utf-8 -*-
"""
Pruebas unitarias para el modulo de Arbol de Directorios (NodoArbol y ArbolDirectorios).

Verifica:
1. Estructura y atributos de NodoArbol (nombre, tipo, hijos, padre, contenido).
2. Restricciones de tipo (carpeta vs archivo).
3. Creacion de la raiz '/'.
4. Creacion de carpetas y archivos (nombres validos, rutas relativas y absolutas).
5. Validacion de duplicados en el mismo nivel.
6. Busqueda recursiva de archivos.
7. Recorrido recursivo en pre-orden.
8. Visualizacion del arbol con indentacion.
9. Eliminacion recursiva en cascada y liberacion de nodos.
10. Navegacion de directorios (cd y pwd).
"""

import unittest
from NodoArbol import NodoArbol
from ArbolDirectorios import ArbolDirectorios


class TestNodoArbol(unittest.TestCase):
    def test_creacion_nodo_carpeta(self):
        nodo = NodoArbol("etc", tipo="carpeta")
        self.assertEqual(nodo.nombre, "etc")
        self.assertEqual(nodo.tipo, NodoArbol.TIPO_CARPETA)
        self.assertIsNone(nodo.padre)
        self.assertEqual(nodo.hijos, [])
        self.assertTrue(nodo.esCarpeta())
        self.assertFalse(nodo.esArchivo())

    def test_creacion_nodo_archivo(self):
        nodo = NodoArbol("config.sys", tipo="archivo", contenido="timeout=10")
        self.assertEqual(nodo.nombre, "config.sys")
        self.assertEqual(nodo.tipo, NodoArbol.TIPO_ARCHIVO)
        self.assertEqual(nodo.contenido, "timeout=10")
        self.assertTrue(nodo.esArchivo())
        self.assertFalse(nodo.esCarpeta())

    def test_tipo_invalido(self):
        with self.assertRaises(ValueError):
            NodoArbol("invalido", tipo="enlace_simbolico")

    def test_agregar_hijo_a_carpeta(self):
        padre = NodoArbol("padre", tipo="carpeta")
        hijo = NodoArbol("hijo.txt", tipo="archivo")
        padre.agregarHijo(hijo)
        self.assertIn(hijo, padre.hijos)
        self.assertEqual(hijo.padre, padre)

    def test_no_permitir_hijo_en_archivo(self):
        archivo = NodoArbol("doc.txt", tipo="archivo")
        otro = NodoArbol("otro.txt", tipo="archivo")
        with self.assertRaises(ValueError):
            archivo.agregarHijo(otro)

    def test_no_permitir_hijo_duplicado(self):
        carpeta = NodoArbol("datos", tipo="carpeta")
        hijo1 = NodoArbol("notas.txt", tipo="archivo")
        hijo2 = NodoArbol("NOTAS.TXT", tipo="archivo")
        carpeta.agregarHijo(hijo1)
        with self.assertRaises(ValueError):
            carpeta.agregarHijo(hijo2)

    def test_obtener_ruta(self):
        raiz = NodoArbol("/", tipo="carpeta")
        usr = NodoArbol("usr", tipo="carpeta")
        bin_dir = NodoArbol("bin", tipo="carpeta")
        app = NodoArbol("app.sh", tipo="archivo")

        raiz.agregarHijo(usr)
        usr.agregarHijo(bin_dir)
        bin_dir.agregarHijo(app)

        self.assertEqual(raiz.obtenerRuta(), "/")
        self.assertEqual(usr.obtenerRuta(), "/usr")
        self.assertEqual(bin_dir.obtenerRuta(), "/usr/bin")
        self.assertEqual(app.obtenerRuta(), "/usr/bin/app.sh")


class TestArbolDirectorios(unittest.TestCase):
    def setUp(self):
        self.arbol = ArbolDirectorios()

    def test_inicializacion_raiz(self):
        self.assertIsNotNone(self.arbol.raiz)
        self.assertEqual(self.arbol.raiz.nombre, "/")
        self.assertEqual(self.arbol.raiz.tipo, NodoArbol.TIPO_CARPETA)
        self.assertIsNone(self.arbol.raiz.padre)
        self.assertEqual(self.arbol.actual, self.arbol.raiz)
        self.assertEqual(self.arbol.obtenerRutaActual(), "/")

    def test_crear_carpeta(self):
        nodo_etc = self.arbol.crearCarpeta("etc")
        self.assertIsNotNone(nodo_etc)
        self.assertEqual(nodo_etc.nombre, "etc")
        self.assertEqual(nodo_etc.obtenerRuta(), "/etc")
        self.assertIn(nodo_etc, self.arbol.raiz.hijos)

        # Crear subcarpeta especificando ruta
        nodo_net = self.arbol.crearCarpeta("network", destino="/etc")
        self.assertIsNotNone(nodo_net)
        self.assertEqual(nodo_net.obtenerRuta(), "/etc/network")
        self.assertEqual(nodo_net.padre, nodo_etc)

    def test_crear_archivo(self):
        self.arbol.crearCarpeta("var")
        archivo = self.arbol.crearArchivo("datos.csv", destino="/var", contenido="id,nombre\n1,santi")
        self.assertIsNotNone(archivo)
        self.assertTrue(archivo.esArchivo())
        self.assertEqual(archivo.obtenerRuta(), "/var/datos.csv")
        self.assertEqual(archivo.contenido, "id,nombre\n1,santi")

    def test_validaciones_nombres_invalidos(self):
        # Nombre vacio
        self.assertIsNone(self.arbol.crearCarpeta(""))
        self.assertIsNone(self.arbol.crearArchivo("  "))

        # Nombre con barra
        self.assertIsNone(self.arbol.crearCarpeta("carpeta/invalida"))
        self.assertIsNone(self.arbol.crearArchivo("archivo/invalido.txt"))

        # Destino inexistente
        self.assertIsNone(self.arbol.crearCarpeta("test", destino="/inexistente"))

    def test_no_permitir_crear_dentro_de_archivo(self):
        self.arbol.crearArchivo("leeme.txt")
        self.assertIsNone(self.arbol.crearCarpeta("sub", destino="/leeme.txt"))
        self.assertIsNone(self.arbol.crearArchivo("otro.txt", destino="/leeme.txt"))

    def test_buscar_archivo_recursivo(self):
        self.arbol.crearCarpeta("home")
        self.arbol.crearCarpeta("usuario", destino="/home")
        self.arbol.crearCarpeta("docs", destino="/home/usuario")
        self.arbol.crearArchivo("tesis.pdf", destino="/home/usuario/docs")

        # Buscar archivo presente en el nivel mas profundo
        encontrado = self.arbol.buscarArchivo("tesis.pdf")
        self.assertIsNotNone(encontrado)
        self.assertEqual(encontrado.obtenerRuta(), "/home/usuario/docs/tesis.pdf")

        # Buscar archivo que no existe
        no_existe = self.arbol.buscarArchivo("fantasma.doc")
        self.assertIsNone(no_existe)

    def test_buscar_todos(self):
        self.arbol.crearCarpeta("folder1")
        self.arbol.crearCarpeta("folder2")
        self.arbol.crearArchivo("log.txt", destino="/folder1")
        self.arbol.crearArchivo("log.txt", destino="/folder2")

        coincidencias = self.arbol.buscarTodos("log.txt")
        self.assertEqual(len(coincidencias), 2)
        rutas = [nodo.obtenerRuta() for nodo in coincidencias]
        self.assertIn("/folder1/log.txt", rutas)
        self.assertIn("/folder2/log.txt", rutas)

    def test_recorrer_recursivamente(self):
        self.arbol.crearCarpeta("a")
        self.arbol.crearCarpeta("b", destino="/a")
        self.arbol.crearArchivo("c.txt", destino="/a/b")

        nombres_visitados = []

        def callback(nodo, nivel):
            nombres_visitados.append((nodo.nombre, nivel))

        nodos = self.arbol.recorrerRecursivamente(funcion_visita=callback)

        self.assertEqual(len(nodos), 4)  # /, a, b, c.txt
        self.assertEqual(nombres_visitados, [
            ("/", 0),
            ("a", 1),
            ("b", 2),
            ("c.txt", 3)
        ])

    def test_mostrar_arbol_con_indentacion(self):
        self.arbol.crearCarpeta("bin")
        self.arbol.crearCarpeta("etc")
        self.arbol.crearArchivo("sh", destino="/bin")

        salida_arbol = self.arbol.mostrarArbol(estilo="arbol", imprimir=False)
        self.assertIn("[DIR] /", salida_arbol)
        self.assertIn("+-- [DIR]  bin", salida_arbol)
        self.assertIn("\\-- [DIR]  etc", salida_arbol)
        self.assertIn("[FILE] sh", salida_arbol)

        salida_simple = self.arbol.mostrarArbol(estilo="simple", imprimir=False)
        self.assertIn("[DIR]  /", salida_simple)
        self.assertIn("    [DIR]  bin", salida_simple)
        self.assertIn("        [FILE] sh", salida_simple)
        self.assertIn("    [DIR]  etc", salida_simple)

    def test_eliminacion_en_cascada(self):
        self.arbol.crearCarpeta("temp")
        self.arbol.crearCarpeta("subtemp", destino="/temp")
        self.arbol.crearArchivo("borrar1.tmp", destino="/temp")
        self.arbol.crearArchivo("borrar2.tmp", destino="/temp/subtemp")

        # Eliminar /temp en cascada
        ok = self.arbol.eliminar("/temp")
        self.assertTrue(ok)

        # Ya no debe existir /temp ni sus descendientes
        self.assertIsNone(self.arbol.obtenerNodoPorRuta("/temp"))
        self.assertIsNone(self.arbol.buscarArchivo("borrar1.tmp"))
        self.assertIsNone(self.arbol.buscarArchivo("borrar2.tmp"))

    def test_prohibir_eliminar_raiz(self):
        ok = self.arbol.eliminar("/")
        self.assertFalse(ok)
        self.assertIn("No esta permitido eliminar el directorio raiz", self.arbol.ultimo_mensaje)

    def test_navegacion_cd_y_pwd(self):
        self.arbol.crearCarpeta("var")
        self.arbol.crearCarpeta("log", destino="/var")

        # cd /var/log
        self.assertTrue(self.arbol.cambiarDirectorio("/var/log"))
        self.assertEqual(self.arbol.obtenerRutaActual(), "/var/log")

        # cd ..
        self.assertTrue(self.arbol.cambiarDirectorio(".."))
        self.assertEqual(self.arbol.obtenerRutaActual(), "/var")

        # cd /
        self.assertTrue(self.arbol.cambiarDirectorio("/"))
        self.assertEqual(self.arbol.obtenerRutaActual(), "/")


if __name__ == "__main__":
    unittest.main()
