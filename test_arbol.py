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

    def test_nodo_liberar_memoria(self):
        padre = NodoArbol("padre", tipo="carpeta")
        hijo = NodoArbol("hijo.txt", tipo="archivo", contenido="texto")
        padre.agregarHijo(hijo)

        hijo.liberar()
        self.assertIsNone(hijo.padre)
        self.assertEqual(hijo.hijos, [])
        self.assertEqual(hijo.contenido, "")


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

    def test_eliminar_archivo_exitoso(self):
        self.arbol.crearCarpeta("docs")
        archivo = self.arbol.crearArchivo("clave.txt", destino="/docs", contenido="secreto")
        self.assertIsNotNone(archivo)

        # Eliminar archivo
        ok = self.arbol.eliminarArchivo("clave.txt", destino="/docs")
        self.assertTrue(ok)
        self.assertIsNone(self.arbol.buscarArchivo("clave.txt"))
        self.assertIsNone(self.arbol.obtenerNodoPorRuta("/docs/clave.txt"))

        # Verificar liberacion de memoria del nodo eliminado (sin referencias)
        self.assertIsNone(archivo.padre)
        self.assertEqual(archivo.hijos, [])
        self.assertEqual(archivo.contenido, "")

    def test_eliminar_archivo_validacion_tipo(self):
        self.arbol.crearCarpeta("musica")
        # Intentar eliminar una carpeta con eliminarArchivo debe fallar
        ok = self.arbol.eliminarArchivo("/musica")
        self.assertFalse(ok)
        self.assertIn("es una carpeta, no un archivo", self.arbol.ultimo_mensaje)

    def test_eliminar_carpeta_sin_cascada_vacia(self):
        self.arbol.crearCarpeta("vacia")
        ok = self.arbol.eliminarCarpeta("/vacia", en_cascada=False)
        self.assertTrue(ok)
        self.assertIsNone(self.arbol.obtenerNodoPorRuta("/vacia"))

    def test_eliminar_carpeta_sin_cascada_con_hijos_falla(self):
        self.arbol.crearCarpeta("no_vacia")
        self.arbol.crearArchivo("hijo.txt", destino="/no_vacia")
        ok = self.arbol.eliminarCarpeta("/no_vacia", en_cascada=False)
        self.assertFalse(ok)
        self.assertIn("no esta vacia", self.arbol.ultimo_mensaje)
        # La carpeta y su hijo siguen existiendo
        self.assertIsNotNone(self.arbol.obtenerNodoPorRuta("/no_vacia"))
        self.assertIsNotNone(self.arbol.buscarArchivo("hijo.txt"))

    def test_eliminar_carpeta_en_cascada_libera_memoria_sin_huerfanos(self):
        # Crear estructura: /a/b/c/archivo.txt
        nodo_a = self.arbol.crearCarpeta("a")
        nodo_b = self.arbol.crearCarpeta("b", destino="/a")
        nodo_c = self.arbol.crearCarpeta("c", destino="/a/b")
        nodo_arc = self.arbol.crearArchivo("archivo.txt", destino="/a/b/c", contenido="datos")

        # Eliminar /a en cascada
        ok = self.arbol.eliminarCarpeta("/a", en_cascada=True)
        self.assertTrue(ok)

        # Verificaciones en el arbol
        self.assertIsNone(self.arbol.obtenerNodoPorRuta("/a"))
        self.assertIsNone(self.arbol.obtenerNodoPorRuta("/a/b"))
        self.assertIsNone(self.arbol.obtenerNodoPorRuta("/a/b/c"))
        self.assertIsNone(self.arbol.buscarArchivo("archivo.txt"))
        self.assertNotIn(nodo_a, self.arbol.raiz.hijos)

        # Verificacion estricta: liberacion de referencias en memoria para cada nodo
        # Ningun nodo debe retener a su padre ni a sus hijos (sin ciclos ni huerfanos)
        self.assertIsNone(nodo_a.padre)
        self.assertEqual(nodo_a.hijos, [])

        self.assertIsNone(nodo_b.padre)
        self.assertEqual(nodo_b.hijos, [])

        self.assertIsNone(nodo_c.padre)
        self.assertEqual(nodo_c.hijos, [])

        self.assertIsNone(nodo_arc.padre)
        self.assertEqual(nodo_arc.hijos, [])
        self.assertEqual(nodo_arc.contenido, "")

    def test_eliminar_carpeta_actualiza_directorio_actual(self):
        self.arbol.crearCarpeta("trabajo")
        self.arbol.crearCarpeta("proyecto1", destino="/trabajo")
        
        # Situarse dentro del directorio que va a ser eliminado
        self.arbol.cambiarDirectorio("/trabajo/proyecto1")
        self.assertEqual(self.arbol.obtenerRutaActual(), "/trabajo/proyecto1")

        # Eliminar /trabajo/proyecto1
        ok = self.arbol.eliminarCarpeta("/trabajo/proyecto1")
        self.assertTrue(ok)

        # self.actual no debe quedar huérfano apuntando al nodo destruido,
        # sino que debe reubicarse en el padre seguro (/trabajo)
        self.assertEqual(self.arbol.obtenerRutaActual(), "/trabajo")

    def test_prohibir_eliminar_raiz_con_eliminar_carpeta(self):
        ok = self.arbol.eliminarCarpeta("/")
        self.assertFalse(ok)
        self.assertIn("No esta permitido eliminar el directorio raiz", self.arbol.ultimo_mensaje)

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


    def test_escenario_documentos(self):
        """Escenario de integracion completo:
        1. Crear carpeta 'Documentos'.
        2. Crear archivo 'tarea.txt' dentro de Documentos.
        3. Buscar 'codigo.cpp' (no existe).
        4. Mostrar todo el arbol.
        5. Eliminar 'Documentos'.
        6. Comprobar que desaparecio todo su subarbol.
        7. Comprobar que no quedaron nodos en memoria (sin huerfanos).
        """
        # --- PASO 1: Crear carpeta 'Documentos' ---
        nodo_docs = self.arbol.crearCarpeta("Documentos")
        self.assertIsNotNone(nodo_docs, "La carpeta 'Documentos' debe crearse sin error.")
        self.assertEqual(nodo_docs.nombre, "Documentos")
        self.assertTrue(nodo_docs.esCarpeta())
        self.assertEqual(nodo_docs.obtenerRuta(), "/Documentos")
        self.assertIn(nodo_docs, self.arbol.raiz.hijos)

        # --- PASO 2: Crear archivo 'tarea.txt' dentro de Documentos ---
        nodo_tarea = self.arbol.crearArchivo(
            "tarea.txt",
            destino="/Documentos",
            contenido="Entregar el lunes"
        )
        self.assertIsNotNone(nodo_tarea, "El archivo 'tarea.txt' debe crearse sin error.")
        self.assertEqual(nodo_tarea.nombre, "tarea.txt")
        self.assertTrue(nodo_tarea.esArchivo())
        self.assertEqual(nodo_tarea.contenido, "Entregar el lunes")
        self.assertEqual(nodo_tarea.obtenerRuta(), "/Documentos/tarea.txt")
        self.assertEqual(nodo_tarea.padre, nodo_docs)
        self.assertIn(nodo_tarea, nodo_docs.hijos)

        # --- PASO 3: Buscar 'codigo.cpp' (no existe) ---
        resultado_busqueda = self.arbol.buscarArchivo("codigo.cpp")
        self.assertIsNone(
            resultado_busqueda,
            "La busqueda de 'codigo.cpp' debe retornar None porque no existe."
        )
        self.assertIn(
            "codigo.cpp",
            self.arbol.ultimo_mensaje,
            "El mensaje de resultado debe mencionar el nombre buscado."
        )

        # --- PASO 4: Mostrar el arbol (sin imprimir en consola durante el test) ---
        representacion = self.arbol.mostrarArbol(estilo="arbol", imprimir=False)
        self.assertIn("[DIR] /", representacion)
        self.assertIn("Documentos", representacion)
        self.assertIn("tarea.txt", representacion)

        # --- PASO 5: Eliminar la carpeta 'Documentos' en cascada ---
        ok = self.arbol.eliminarCarpeta("/Documentos", en_cascada=True)
        self.assertTrue(ok, "La eliminacion de 'Documentos' debe ser exitosa.")

        # --- PASO 6: Comprobar que desaparecio todo el subarbol del arbol ---
        self.assertIsNone(
            self.arbol.obtenerNodoPorRuta("/Documentos"),
            "'Documentos' no debe existir en el arbol tras la eliminacion."
        )
        self.assertIsNone(
            self.arbol.buscarArchivo("tarea.txt"),
            "'tarea.txt' no debe existir en el arbol tras la eliminacion."
        )
        self.assertNotIn(
            nodo_docs,
            self.arbol.raiz.hijos,
            "'Documentos' no debe aparecer como hijo de la raiz."
        )

        # --- PASO 7: Comprobar que no quedaron nodos en memoria ---
        # Verificar nodo_docs: sin padre, sin hijos (lista limpia)
        self.assertIsNone(
            nodo_docs.padre,
            "nodo_docs.padre debe ser None tras la liberacion."
        )
        self.assertEqual(
            nodo_docs.hijos,
            [],
            "nodo_docs.hijos debe estar vacia tras la liberacion."
        )

        # Verificar nodo_tarea: sin padre, sin hijos, sin contenido
        self.assertIsNone(
            nodo_tarea.padre,
            "nodo_tarea.padre debe ser None tras la liberacion."
        )
        self.assertEqual(
            nodo_tarea.hijos,
            [],
            "nodo_tarea.hijos debe estar vacia tras la liberacion."
        )
        self.assertEqual(
            nodo_tarea.contenido,
            "",
            "nodo_tarea.contenido debe estar vacio tras la liberacion."
        )

        # Confirmar que el arbol raiz quedo limpio y vacio
        self.assertEqual(
            len(self.arbol.raiz.hijos),
            0,
            "La raiz no debe tener hijos tras eliminar 'Documentos'."
        )


if __name__ == "__main__":
    unittest.main()
