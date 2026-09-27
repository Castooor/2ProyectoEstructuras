# -*- coding: utf-8 -*-
"""
Entidad 'NodoUsuario': la entrada (credencial) de un usuario guardada en la
tabla hash.

Vive en su propio archivo por el principio de responsabilidad unica (SRP):
esta clase solo representa al usuario y actua como nodo de la lista simple
que resuelve las colisiones. El calculo del indice, la dispersion (funcion
hash) y la autenticacion pertenecen a 'TablaHash' (TablaHash.py).
"""


class NodoUsuario:
    """Entrada de usuario: un nodo de la lista simple de un indice.

    Cada indice de la tabla apunta al primer nodo de su cadena (o a None si
    esta libre); el resto de usuarios que colisionan se enlazan con
    'siguiente'. Esta es la lista simple que se usa para resolver colisiones.

    Atributos:
        nombre (str): nombre de usuario, tal como lo escribio la persona.
        contrasena (str): contrasena de acceso.
        rol (str): perfil de permisos ('usuario', 'administrador', ...).
        siguiente (NodoUsuario | None): enlace al siguiente nodo de la cadena.
    """

    def __init__(self, nombre, contrasena, rol="usuario"):
        self.nombre = nombre
        self.contrasena = contrasena
        self.rol = rol
        self.siguiente = None

    def __repr__(self):
        return "NodoUsuario(nombre='%s', rol='%s')" % (self.nombre, self.rol)
