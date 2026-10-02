# -*- coding: utf-8 -*-
"""
Entidad 'NodoArbol': representa un elemento del sistema de archivos interno de
un servidor (disco duro virtual).

Siguiendo el principio de responsabilidad unica (SRP), esta clase modela
exclusivamente el nodo y sus relaciones de parentesco (padre e hijos). La
logica global del arbol, navegacion y gestion jerarquica reside en
'ArbolDirectorios' (ArbolDirectorios.py).
"""


class NodoArbol:
    """Nodo para la estructura de arbol general de directorios y archivos.

    Un nodo puede ser de tipo 'carpeta' (nodo interno que puede albergar otros
    nodos hijos) o de tipo 'archivo' (nodo hoja que contiene datos).

    Atributos:
        nombre (str): Nombre del directorio o archivo (ej. 'etc', 'servidor.conf').
        tipo (str): Tipo de elemento ('carpeta' o 'archivo').
        padre (NodoArbol | None): Referencia al nodo directorio contenedor.
            Para la raiz ('/'), el padre es None.
        hijos (list[NodoArbol]): Lista dinamica de nodos hijos pertenecientes
            a esta carpeta. Si es un archivo, permanece vacia.
        contenido (str): Contenido textual opcional para archivos.
    """

    TIPO_CARPETA = "carpeta"
    TIPO_ARCHIVO = "archivo"

    def __init__(self, nombre, tipo="carpeta", padre=None, contenido=""):
        tipo_normalizado = tipo.strip().lower()
        if tipo_normalizado not in (self.TIPO_CARPETA, self.TIPO_ARCHIVO):
            raise ValueError(
                "Tipo de nodo invalido '%s'. Debe ser '%s' o '%s'."
                % (tipo, self.TIPO_CARPETA, self.TIPO_ARCHIVO)
            )

        self.nombre = nombre
        self.tipo = tipo_normalizado
        self.padre = padre
        self.hijos = []
        self.contenido = contenido if self.tipo == self.TIPO_ARCHIVO else ""

    # ------------------------------------------------------------------
    # Consultas de estado
    # ------------------------------------------------------------------
    def esCarpeta(self):
        """Retorna True si el nodo corresponde a un directorio / carpeta."""
        return self.tipo == self.TIPO_CARPETA

    def esArchivo(self):
        """Retorna True si el nodo corresponde a un archivo (nodo hoja)."""
        return self.tipo == self.TIPO_ARCHIVO

    def esRaiz(self):
        """Retorna True si el nodo es la raiz del arbol (no tiene padre)."""
        return self.padre is None and self.nombre == "/"

    # ------------------------------------------------------------------
    # Manejo de hijos
    # ------------------------------------------------------------------
    def agregarHijo(self, nodo_hijo):
        """Agrega un nodo hijo a este directorio.

        Lanza ValueError si este nodo es un archivo o si ya existe un hijo
        con el mismo nombre en este nivel.
        """
        if self.esArchivo():
            raise ValueError(
                "No se pueden agregar elementos dentro del archivo '%s'." % self.nombre
            )

        if not isinstance(nodo_hijo, NodoArbol):
            raise TypeError("El hijo debe ser una instancia de NodoArbol.")

        # Validacion de nombres duplicados en el mismo directorio
        for hijo in self.hijos:
            if hijo.nombre.lower() == nodo_hijo.nombre.lower():
                raise ValueError(
                    "Ya existe un elemento con el nombre '%s' en '%s'."
                    % (nodo_hijo.nombre, self.nombre)
                )

        nodo_hijo.padre = self
        self.hijos.append(nodo_hijo)

    def eliminarHijo(self, nodo_hijo):
        """Remueve un nodo hijo de la lista de hijos si existe."""
        if nodo_hijo in self.hijos:
            self.hijos.remove(nodo_hijo)
            nodo_hijo.padre = None
            return True
        return False

    def buscarHijoDirecto(self, nombre):
        """Busca un hijo inmediato por su nombre (no recursivo).

        Retorna el NodoArbol correspondiente o None si no existe.
        """
        nombre_buscar = nombre.strip().lower()
        for hijo in self.hijos:
            if hijo.nombre.strip().lower() == nombre_buscar:
                return hijo
        return None

    # ------------------------------------------------------------------
    # Representacion y rutas
    # ------------------------------------------------------------------
    def obtenerRuta(self):
        """Construye y devuelve la ruta absoluta del nodo (ej. '/var/log/syslog')."""
        if self.padre is None:
            return self.nombre  # Normalmente '/'

        partes = []
        actual = self
        while actual is not None and actual.padre is not None:
            partes.append(actual.nombre)
            actual = actual.padre

        partes.reverse()
        return "/" + "/".join(partes)

    def __repr__(self):
        return "NodoArbol(nombre='%s', tipo='%s', hijos=%d)" % (
            self.nombre,
            self.tipo,
            len(self.hijos),
        )

    def __str__(self):
        etiqueta = "DIR" if self.esCarpeta() else "FILE"
        return "[%s] %s" % (etiqueta, self.nombre)
