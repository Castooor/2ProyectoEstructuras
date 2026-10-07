# -*- coding: utf-8 -*-

class NodoArbol:

    TIPO_CARPETA = "carpeta"
    TIPO_ARCHIVO = "archivo"

    def __init__(self, nombre, tipo="carpeta", padre=None, contenido=""):
        tipo_normalizado = tipo.strip().lower()

        if tipo_normalizado not in (
            self.TIPO_CARPETA,
            self.TIPO_ARCHIVO
        ):
            raise ValueError(
                "Tipo de nodo invalido '%s'. Debe ser '%s' o '%s'."
                % (tipo, self.TIPO_CARPETA, self.TIPO_ARCHIVO)
            )

        self.nombre = nombre
        self.tipo = tipo_normalizado
        self.padre = padre
        self.hijos = []
        self.contenido = (
            contenido
            if self.tipo == self.TIPO_ARCHIVO
            else ""
        )

    def esCarpeta(self):
        return self.tipo == self.TIPO_CARPETA

    def esArchivo(self):
        return self.tipo == self.TIPO_ARCHIVO

    def esRaiz(self):
        return self.padre is None and self.nombre == "/"

    def agregarHijo(self, nodo_hijo):
        if self.esArchivo():
            raise ValueError(
                "No se pueden agregar elementos dentro del archivo '%s'."
                % self.nombre
            )

        if not isinstance(nodo_hijo, NodoArbol):
            raise TypeError(
                "El hijo debe ser una instancia de NodoArbol."
            )

        for hijo in self.hijos:
            if hijo.nombre.lower() == nodo_hijo.nombre.lower():
                raise ValueError(
                    "Ya existe un elemento con el nombre '%s' en '%s'."
                    % (nodo_hijo.nombre, self.nombre)
                )

        nodo_hijo.padre = self
        self.hijos.append(nodo_hijo)

    def eliminarHijo(self, nodo_hijo):
        if nodo_hijo in self.hijos:
            self.hijos.remove(nodo_hijo)
            nodo_hijo.padre = None
            return True

        return False

    def buscarHijoDirecto(self, nombre):
        nombre_buscar = nombre.strip().lower()

        for hijo in self.hijos:
            if hijo.nombre.strip().lower() == nombre_buscar:
                return hijo

        return None

    def obtenerRuta(self):
        if self.padre is None:
            return self.nombre

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