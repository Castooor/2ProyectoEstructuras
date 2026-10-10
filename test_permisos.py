# -*- coding: utf-8 -*-
"""
Pruebas de autenticación, permisos por rol y menús.

Ejecutar desde la raíz del proyecto:
    python -m unittest test_permisos.py
"""
import contextlib
import io
import os
import tempfile
import unittest
from unittest import mock

import main as sistema
from ArbolDirectorios import ArbolDirectorios
from GrafoServidores import GrafoServidores
from TablaHash import TablaHash
from auditoria import Auditoria


class TestRolesEnTablaHash(unittest.TestCase):
    def setUp(self):
        self.tabla = TablaHash()
        self.tabla.registrarUsuario("kenan", "Kenan123", "administrador")
        self.tabla.registrarUsuario("allison", "Allison123", "usuario")
        self.eventos = []

    def test_rol_invalido_se_rechaza(self):
        with self.assertRaises(ValueError):
            self.tabla.registrarUsuario("intruso", "x123", "superroot")
        self.assertNotIn("intruso", self.tabla)

    def test_rol_se_normaliza(self):
        self.tabla.registrarUsuario("brayan", "Brayan123", " Administrador ")
        self.assertEqual(self.tabla.buscarUsuario("brayan").rol, "administrador")

    def test_sin_sesion_no_es_administrador(self):
        self.assertFalse(self.tabla.esAdministrador())
        self.assertFalse(self.tabla.verificarPermiso("crear carpeta"))

    def test_usuario_normal_no_tiene_permiso(self):
        self.tabla.iniciarSesion("allison", "Allison123")
        self.assertFalse(self.tabla.esAdministrador())
        self.assertFalse(self.tabla.verificarPermiso(
            "eliminar carpeta", registrar_evento=self.eventos.append))
        self.assertIn("Acceso denegado", self.tabla.ultimo_mensaje)
        self.assertEqual(len(self.eventos), 1)
        self.assertIn("allison", self.eventos[0])

    def test_administrador_tiene_permiso(self):
        self.tabla.iniciarSesion("kenan", "Kenan123")
        self.assertTrue(self.tabla.esAdministrador())
        self.assertTrue(self.tabla.verificarPermiso(
            "eliminar carpeta", registrar_evento=self.eventos.append))
        self.assertEqual(self.eventos, [])

    def test_cerrar_sesion_quita_el_permiso(self):
        self.tabla.iniciarSesion("kenan", "Kenan123")
        self.tabla.cerrarSesion()
        self.assertFalse(self.tabla.esAdministrador())


class TestAccionesPorRol(unittest.TestCase):
    def setUp(self):
        with tempfile.TemporaryDirectory() as carpeta:
            auditoria = Auditoria(os.path.join(carpeta, "log.txt"))
            self.acciones = sistema.definir_acciones(
                ArbolDirectorios(), TablaHash(), auditoria, GrafoServidores())

    def descripciones(self, es_admin):
        return [a.descripcion for a in sistema.acciones_para_rol(self.acciones, es_admin)]

    def test_administrador_ve_todo(self):
        self.assertEqual(len(self.descripciones(True)), len(self.acciones))

    def test_usuario_no_ve_acciones_delicadas(self):
        visibles = self.descripciones(False)
        for delicada in ("Crear carpeta", "Crear archivo", "Eliminar archivo",
                         "Eliminar carpeta", "Registrar usuario", "Eliminar usuario"):
            self.assertNotIn(delicada, visibles)

    def test_usuario_conserva_las_consultas(self):
        visibles = self.descripciones(False)
        for consulta in ("Buscar archivo", "Mostrar árbol", "Cambiar directorio",
                         "Mostrar ruta actual", "Mostrar usuario activo",
                         "Red y enrutamiento"):
            self.assertIn(consulta, visibles)

    def test_todo_lo_que_crea_o_borra_es_solo_admin(self):
        for accion in self.acciones:
            texto = accion.descripcion.lower()
            if texto.startswith(("crear", "eliminar", "registrar")):
                self.assertTrue(accion.solo_admin, accion.descripcion)


class TestFlujoDeSesion(unittest.TestCase):
    """Ejecuta main() con entradas simuladas y revisa lo que se imprime."""

    def ejecutar(self, entradas):
        iterador = iter(entradas)

        def falso_input(_mensaje=""):
            try:
                return next(iterador)
            except StopIteration:
                raise EOFError

        salida = io.StringIO()
        with tempfile.TemporaryDirectory() as carpeta:
            archivo = os.path.join(carpeta, "log.txt")
            with mock.patch("builtins.input", falso_input), \
                    contextlib.redirect_stdout(salida):
                sistema.main(archivo_auditoria=archivo)
            with open(archivo, encoding="utf-8") as f:
                log = f.read()
        return salida.getvalue(), log

    def test_el_primer_menu_solo_ofrece_iniciar_sesion_y_salir(self):
        texto, _ = self.ejecutar(["2"])
        self.assertIn("1. Iniciar sesión", texto)
        self.assertIn("2. Salir", texto)
        self.assertNotIn("Crear carpeta", texto)
        self.assertNotIn("Buscar archivo", texto)

    def test_sin_sesion_no_se_puede_usar_el_sistema(self):
        # "3" no existe en el menú de inicio; tampoco se llega al menú de archivos.
        texto, _ = self.ejecutar(["3", "2"])
        self.assertIn("Opción inválida", texto)
        self.assertNotIn("Crear carpeta", texto)

    def test_login_fallido_vuelve_al_inicio_con_mensaje_generico(self):
        texto, log = self.ejecutar(["1", "admin", "mala", "1", "fantasma", "x", "2"])
        self.assertEqual(texto.count("Usuario o contraseña incorrectos."), 2)
        self.assertNotIn("Crear carpeta", texto)
        self.assertIn("contrasena incorrecta", log)
        self.assertIn("usuario inexistente", log)

    def test_administrador_ve_el_menu_completo(self):
        texto, _ = self.ejecutar(["1", "admin", "admin123", "0", "2"])
        self.assertIn("Usuario: admin | Rol: administrador", texto)
        for opcion in ("Crear carpeta", "Eliminar carpeta", "Registrar usuario",
                       "Eliminar usuario", "Ver auditoría"):
            self.assertIn(opcion, texto)

    def test_usuario_ve_solo_el_menu_reducido(self):
        entradas = [
            "1", "admin", "admin123",          # entra el administrador
            "9", "ana", "Ana12345", "1",       # registra a 'ana' como usuario
            "0",                               # cierra sesión
            "1", "ana", "Ana12345",            # entra 'ana'
            "0",                               # cierra sesión
            "2",                               # sale
        ]
        texto, _ = self.ejecutar(entradas)
        partes = texto.split("Usuario: ana | Rol: usuario")
        self.assertEqual(len(partes), 2)
        menu_usuario = partes[1].split("0. Cerrar sesión")[0]
        for visible in ("Buscar archivo", "Mostrar árbol", "Red y enrutamiento"):
            self.assertIn(visible, menu_usuario)
        for oculta in ("Crear carpeta", "Crear archivo", "Eliminar archivo",
                       "Eliminar carpeta", "Registrar usuario", "Eliminar usuario",
                       "Mostrar tabla hash", "Ver auditoría"):
            self.assertNotIn(oculta, menu_usuario)

    def test_admin_no_puede_eliminar_su_propia_cuenta(self):
        entradas = ["1", "admin", "admin123", "10", "admin", "0", "2"]
        texto, _ = self.ejecutar(entradas)
        self.assertIn("No puede eliminar la cuenta con la que tiene la sesión abierta", texto)

    def test_admin_elimina_a_otro_usuario_y_este_ya_no_entra(self):
        entradas = [
            "1", "admin", "admin123",
            "9", "ana", "Ana12345", "1",
            "10", "ana", "s",
            "0",
            "1", "ana", "Ana12345",
            "2",
        ]
        texto, log = self.ejecutar(entradas)
        self.assertIn("Eliminacion de usuario: ana", log)
        self.assertIn("Usuario o contraseña incorrectos.", texto)

    def test_el_cierre_de_sesion_regresa_al_menu_de_inicio(self):
        texto, log = self.ejecutar(["1", "admin", "admin123", "0", "2"])
        self.assertIn("Sesión cerrada: admin", texto)
        self.assertIn("Cierre de sesion: admin", log)

    def test_red_en_modo_consulta_bloquea_modificaciones(self):
        entradas = [
            "1", "admin", "admin123",
            "9", "ana", "Ana12345", "1", "0",
            "1", "ana", "Ana12345",
            "6", "1", "0",                     # abre 'Red', intenta opción 1, vuelve
            "0", "2",
        ]
        texto, _ = self.ejecutar(entradas)
        self.assertIn("Modo consulta", texto)
        self.assertIn("Acción no permitida para su rol.", texto)
        self.assertNotIn("1. Agregar servidor", texto.split("Modo consulta")[1].split("0. Volver")[0])


if __name__ == "__main__":
    unittest.main()
