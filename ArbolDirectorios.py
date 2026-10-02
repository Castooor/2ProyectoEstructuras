# -*- coding: utf-8 -*-
"""
Estructura de Datos: 'ArbolDirectorios' (Arbol General de Directorios).

Simula el disco duro interno de un servidor en el sistema operativo de red
(Network OS). Implementa una jerarquia de archivos y carpetas a partir de
un nodo raiz principal ('/').

Operaciones implementadas:
- Inicializacion con raiz ('/').
- Crear carpeta (nodo interno).
- Crear archivo (nodo hoja).
- Buscar archivo recursivamente por nombre en todas las ramas.
- Recorrer el arbol recursivamente (pre-orden, con funcion de visita opcional).
- Mostrar el arbol en consola con indentacion adecuada (estilo texto y ramas visuales).
- Eliminacion recursiva en cascada (limpieza de memoria desde las hojas sin nodos huerfanos).
- Resolucion y navegacion de rutas absolutas y relativas.
"""

from NodoArbol import NodoArbol


class ArbolDirectorios:
    """Arbol general para la administracion jerarquica de carpetas y archivos.

    Atributos:
        raiz (NodoArbol): Nodo principal que representa la raiz del disco ('/').
        actual (NodoArbol): Directorio de trabajo actual para operaciones relativas.
        ultimo_mensaje (str): Descripcion del resultado de la ultima operacion efectuada.
    """

    def __init__(self):
        # Crear la raiz '/' como carpeta principal
        self.raiz = NodoArbol(nombre="/", tipo=NodoArbol.TIPO_CARPETA, padre=None)
        self.actual = self.raiz
        self.ultimo_mensaje = "Sistema de directorios inicializado con raiz '/'."

    # ------------------------------------------------------------------
    # 1) RESOLUCION DE RUTAS Y NODOS
    # ------------------------------------------------------------------
    def resolverNodo(self, destino=None):
        """Obtiene un NodoArbol a partir de una instancia existente o una ruta en string.

        Si destino es None, devuelve el directorio de trabajo actual (self.actual).
        Si destino es un string, busca el nodo navegando la ruta absoluta o relativa.
        Si destino ya es un NodoArbol, lo devuelve directamente.
        """
        if destino is None:
            return self.actual

        if isinstance(destino, NodoArbol):
            return destino

        if isinstance(destino, str):
            return self.obtenerNodoPorRuta(destino)

        return None

    def obtenerNodoPorRuta(self, ruta):
        """Busca y retorna el nodo correspondiente a una ruta (absoluta o relativa).

        Ejemplos de ruta:
          - '/' -> Raiz
          - '/var/log/syslog' -> Ruta absoluta
          - 'documentos/trabajos' -> Ruta relativa desde self.actual
          - '..' -> Carpeta padre
        """
        if not ruta or not isinstance(ruta, str):
            return None

        ruta_limpia = ruta.strip()
        if ruta_limpia == "/":
            return self.raiz

        # Determinar punto de partida: raiz si inicia con '/', o nodo actual si es relativa
        if ruta_limpia.startswith("/"):
            nodo_cursor = self.raiz
            partes = [p for p in ruta_limpia.split("/") if p]
        else:
            nodo_cursor = self.actual
            partes = [p for p in ruta_limpia.split("/") if p]

        for parte in partes:
            if parte == ".":
                continue
            elif parte == "..":
                if nodo_cursor.padre is not None:
                    nodo_cursor = nodo_cursor.padre
            else:
                if nodo_cursor.esArchivo():
                    return None  # Un archivo no contiene subelementos
                hijo_encontrado = nodo_cursor.buscarHijoDirecto(parte)
                if hijo_encontrado is None:
                    return None
                nodo_cursor = hijo_encontrado

        return nodo_cursor

    # ------------------------------------------------------------------
    # 2) OPERACIONES DE CREACION
    # ------------------------------------------------------------------
    def crearCarpeta(self, nombre, destino=None, registrar_evento=None):
        """Crea una nueva carpeta dentro del nodo o ruta destino especificada.

        Parametros:
            nombre (str): Nombre de la carpeta a crear.
            destino (NodoArbol | str | None): Carpeta padre donde se creara.
                Por defecto se crea en el directorio actual.
            registrar_evento (callable | None): Callback opcional para auditoria.

        Retorna:
            NodoArbol | None: El nuevo nodo creado o None si fallo.
        """
        nombre_limpio = nombre.strip() if isinstance(nombre, str) else ""
        if not nombre_limpio:
            self.ultimo_mensaje = "Error: El nombre de la carpeta no puede estar vacio."
            return None

        if "/" in nombre_limpio:
            self.ultimo_mensaje = "Error: El nombre de la carpeta no puede contener '/'."
            return None

        padre = self.resolverNodo(destino)
        if padre is None:
            self.ultimo_mensaje = "Error: El directorio destino no existe."
            return None

        if padre.esArchivo():
            self.ultimo_mensaje = (
                "Error: No se puede crear una carpeta dentro de un archivo ('%s')."
                % padre.nombre
            )
            return None

        if padre.buscarHijoDirecto(nombre_limpio) is not None:
            self.ultimo_mensaje = (
                "Error: Ya existe un elemento llamado '%s' en '%s'."
                % (nombre_limpio, padre.obtenerRuta())
            )
            return None

        nueva_carpeta = NodoArbol(
            nombre=nombre_limpio,
            tipo=NodoArbol.TIPO_CARPETA,
            padre=padre
        )
        padre.agregarHijo(nueva_carpeta)
        self.ultimo_mensaje = (
            "Carpeta '%s' creada exitosamente en '%s'."
            % (nombre_limpio, padre.obtenerRuta())
        )

        if registrar_evento:
            registrar_evento("[ARBOL] Creacion de carpeta: %s" % nueva_carpeta.obtenerRuta())

        return nueva_carpeta

    def crearArchivo(self, nombre, destino=None, contenido="", registrar_evento=None):
        """Crea un nuevo archivo dentro del nodo o ruta destino especificada.

        Parametros:
            nombre (str): Nombre del archivo a crear (ej. 'datos.txt').
            destino (NodoArbol | str | None): Carpeta donde se creara.
                Por defecto se crea en el directorio actual.
            contenido (str): Contenido textual del archivo.
            registrar_evento (callable | None): Callback opcional para auditoria.

        Retorna:
            NodoArbol | None: El nuevo nodo creado o None si fallo.
        """
        nombre_limpio = nombre.strip() if isinstance(nombre, str) else ""
        if not nombre_limpio:
            self.ultimo_mensaje = "Error: El nombre del archivo no puede estar vacio."
            return None

        if "/" in nombre_limpio:
            self.ultimo_mensaje = "Error: El nombre del archivo no puede contener '/'."
            return None

        padre = self.resolverNodo(destino)
        if padre is None:
            self.ultimo_mensaje = "Error: El directorio destino no existe."
            return None

        if padre.esArchivo():
            self.ultimo_mensaje = (
                "Error: No se puede crear un archivo dentro de otro archivo ('%s')."
                % padre.nombre
            )
            return None

        if padre.buscarHijoDirecto(nombre_limpio) is not None:
            self.ultimo_mensaje = (
                "Error: Ya existe un elemento llamado '%s' en '%s'."
                % (nombre_limpio, padre.obtenerRuta())
            )
            return None

        nuevo_archivo = NodoArbol(
            nombre=nombre_limpio,
            tipo=NodoArbol.TIPO_ARCHIVO,
            padre=padre,
            contenido=contenido
        )
        padre.agregarHijo(nuevo_archivo)
        self.ultimo_mensaje = (
            "Archivo '%s' creado exitosamente en '%s'."
            % (nombre_limpio, padre.obtenerRuta())
        )

        if registrar_evento:
            registrar_evento("[ARBOL] Creacion de archivo: %s" % nuevo_archivo.obtenerRuta())

        return nuevo_archivo

    # ------------------------------------------------------------------
    # 3) BUSQUEDA RECURSIVA DE ARCHIVOS
    # ------------------------------------------------------------------
    def buscarArchivo(self, nombre, nodo_inicio=None):
        """Busca recursivamente el primer archivo con el nombre especificado.

        Recorre las ramas del arbol a partir de 'nodo_inicio' (o de la raiz
        si no se indica).

        Retorna:
            NodoArbol | None: El nodo del archivo si se encontro, o None.
        """
        nombre_buscar = nombre.strip().lower() if isinstance(nombre, str) else ""
        if not nombre_buscar:
            self.ultimo_mensaje = "Error: Ingrese un nombre de archivo a buscar."
            return None

        raiz_busqueda = self.resolverNodo(nodo_inicio) or self.raiz
        encontrado = self._buscarArchivoRecursivo(raiz_busqueda, nombre_buscar)

        if encontrado:
            self.ultimo_mensaje = (
                "Archivo '%s' encontrado en la ruta: %s"
                % (encontrado.nombre, encontrado.obtenerRuta())
            )
        else:
            self.ultimo_mensaje = (
                "Archivo '%s' no encontrado en el subarbol '%s'."
                % (nombre, raiz_busqueda.obtenerRuta())
            )
        return encontrado

    def _buscarArchivoRecursivo(self, nodo_actual, nombre_buscar):
        """Metodo auxiliar recursivo para buscar un archivo navegando por las ramas."""
        # Caso base 1: El nodo actual es un archivo y su nombre coincide
        if nodo_actual.esArchivo():
            if nodo_actual.nombre.strip().lower() == nombre_buscar:
                return nodo_actual
            return None

        # Caso recursivo: Si es carpeta, buscar en cada uno de sus hijos
        for hijo in nodo_actual.hijos:
            resultado = self._buscarArchivoRecursivo(hijo, nombre_buscar)
            if resultado is not None:
                return resultado

        # No se encontro en este subarbol
        return None

    def buscarTodos(self, nombre, nodo_inicio=None, solo_archivos=True):
        """Busca recursivamente todas las coincidencias con el nombre indicado.

        Dado que en distintas carpetas pueden existir archivos o subcarpetas
        con igual denominacion, este metodo retorna una lista con todos los
        nodos que coincidan.
        """
        nombre_buscar = nombre.strip().lower() if isinstance(nombre, str) else ""
        if not nombre_buscar:
            return []

        raiz_busqueda = self.resolverNodo(nodo_inicio) or self.raiz
        coincidencias = []
        self._buscarTodosRecursivo(raiz_busqueda, nombre_buscar, solo_archivos, coincidencias)
        return coincidencias

    def _buscarTodosRecursivo(self, nodo_actual, nombre_buscar, solo_archivos, lista_resultados):
        """Recorrido recursivo acumulador de coincidencias."""
        coincide_nombre = nodo_actual.nombre.strip().lower() == nombre_buscar
        if coincide_nombre:
            if not solo_archivos or nodo_actual.esArchivo():
                lista_resultados.append(nodo_actual)

        if nodo_actual.esCarpeta():
            for hijo in nodo_actual.hijos:
                self._buscarTodosRecursivo(hijo, nombre_buscar, solo_archivos, lista_resultados)

    # ------------------------------------------------------------------
    # 4) RECORRIDO RECURSIVO DEL ARBOL
    # ------------------------------------------------------------------
    def recorrerRecursivamente(self, nodo_inicio=None, funcion_visita=None):
        """Recorre el arbol de forma recursiva en pre-orden.

        Visita primero el nodo contenedor y luego profundiza recursivamente
        en cada uno de sus hijos.

        Parametros:
            nodo_inicio (NodoArbol | str | None): Punto de inicio (por defecto la raiz).
            funcion_visita (callable | None): Funcion opcional con firma
                funcion_visita(nodo, nivel) que se ejecuta en cada visita.

        Retorna:
            list[NodoArbol]: Lista de todos los nodos visitados en orden.
        """
        raiz_recorrido = self.resolverNodo(nodo_inicio) or self.raiz
        nodos_visitados = []
        self._recorrerRecursivo(raiz_recorrido, 0, funcion_visita, nodos_visitados)
        return nodos_visitados

    def _recorrerRecursivo(self, nodo_actual, nivel, funcion_visita, lista_acumuladora):
        """Implementacion recursiva del recorrido en pre-orden."""
        # 1. Visitar nodo actual
        lista_acumuladora.append(nodo_actual)
        if funcion_visita:
            funcion_visita(nodo_actual, nivel)

        # 2. Paso recursivo: Visitar secuencialmente cada hijo
        if nodo_actual.esCarpeta():
            for hijo in nodo_actual.hijos:
                self._recorrerRecursivo(hijo, nivel + 1, funcion_visita, lista_acumuladora)

    # ------------------------------------------------------------------
    # 5) MOSTRAR EL ARBOL CON INDENTACION
    # ------------------------------------------------------------------
    def mostrarArbol(self, nodo_inicio=None, estilo="arbol", imprimir=True, destino=None):
        """Muestra la jerarquia del arbol con indentacion en consola.

        Parametros:
            nodo_inicio (NodoArbol | str | None): Subarbol a mostrar (def: raiz).
            estilo (str):
                - 'arbol': Muestra con conectores jerarquicos (+--, \\--, |  ).
                - 'simple': Muestra con sangria de espacios y prefijos [DIR]/[FILE].
                - 'unicode': Muestra con ramas graficas Unicode (├──, └──, │  ).
            imprimir (bool): Si es True, hace print() en pantalla. Siempre
                retorna la cadena formateada.
            destino (NodoArbol | str | None): Alias de nodo_inicio por compatibilidad.

        Retorna:
            str: Representacion textual del arbol.
        """
        punto_inicio = nodo_inicio if nodo_inicio is not None else destino
        raiz_subarbol = self.resolverNodo(punto_inicio) or self.raiz
        lineas = []

        if estilo == "simple":
            self._construirSimple(raiz_subarbol, 0, lineas)
        elif estilo == "unicode":
            self._construirVisualUnicode(raiz_subarbol, "", True, lineas, raiz_subarbol)
        else:
            # Estilo por defecto 'arbol' con caracteres ASCII seguros para cualquier consola
            self._construirVisualAscii(raiz_subarbol, "", True, lineas, raiz_subarbol)

        resultado = "\n".join(lineas)
        if imprimir:
            print(resultado)
        return resultado

    def _construirSimple(self, nodo, nivel, lineas):
        """Construye representacion indentada con sangria simple."""
        sangria = "    " * nivel
        icono = "[DIR] " if nodo.esCarpeta() else "[FILE]"
        lineas.append("%s%s %s" % (sangria, icono, nodo.nombre))

        if nodo.esCarpeta():
            for hijo in nodo.hijos:
                self._construirSimple(hijo, nivel + 1, lineas)

    def _construirVisualAscii(self, nodo, prefijo, es_ultimo, lineas, raiz_subarbol):
        """Construye representacion jerarquica usando conectores ASCII (+--, \\--, |  )."""
        icono = "[DIR] " if nodo.esCarpeta() else "[FILE]"
        if nodo == raiz_subarbol:
            lineas.append("%s%s" % (icono, nodo.nombre))
            nuevo_prefijo = ""
        else:
            conector = "\\-- " if es_ultimo else "+-- "
            lineas.append("%s%s%s %s" % (prefijo, conector, icono, nodo.nombre))
            nuevo_prefijo = prefijo + ("    " if es_ultimo else "|   ")

        if nodo.esCarpeta():
            total_hijos = len(nodo.hijos)
            for indice, hijo in enumerate(nodo.hijos):
                ultimo_del_grupo = (indice == total_hijos - 1)
                self._construirVisualAscii(hijo, nuevo_prefijo, ultimo_del_grupo, lineas, raiz_subarbol)

    def _construirVisualUnicode(self, nodo, prefijo, es_ultimo, lineas, raiz_subarbol):
        """Construye representacion jerarquica usando conectores Unicode (├──, └──, │  )."""
        icono = "[DIR] " if nodo.esCarpeta() else "[FILE]"
        if nodo == raiz_subarbol:
            lineas.append("%s%s" % (icono, nodo.nombre))
            nuevo_prefijo = ""
        else:
            conector = "└── " if es_ultimo else "├── "
            lineas.append("%s%s%s %s" % (prefijo, conector, icono, nodo.nombre))
            nuevo_prefijo = prefijo + ("    " if es_ultimo else "│   ")

        if nodo.esCarpeta():
            total_hijos = len(nodo.hijos)
            for indice, hijo in enumerate(nodo.hijos):
                ultimo_del_grupo = (indice == total_hijos - 1)
                self._construirVisualUnicode(hijo, nuevo_prefijo, ultimo_del_grupo, lineas, raiz_subarbol)

    # ------------------------------------------------------------------
    # 6) ELIMINACION EN CASCADA (Liberacion recursiva estricta)
    # ------------------------------------------------------------------
    def eliminar(self, destino, registrar_evento=None):
        """Elimina un archivo o carpeta del arbol.

        Si se elimina una carpeta, se ejecuta una eliminacion en cascada
        estricta en post-orden: recorre recursivamente el subarbol liberando
        primero las hojas y desconectando punteros de abajo hacia arriba
        para no dejar nodos huerfanos en memoria.

        Parametros:
            destino (NodoArbol | str): Nodo o ruta a eliminar.
            registrar_evento (callable | None): Callback para auditoria.

        Retorna:
            bool: True si se elimino con exito, False si fallo.
        """
        nodo = self.resolverNodo(destino)
        if nodo is None:
            self.ultimo_mensaje = "Error: El elemento a eliminar no existe."
            return False

        if nodo.esRaiz():
            self.ultimo_mensaje = "Error: No esta permitido eliminar el directorio raiz '/'."
            return False

        padre = nodo.padre
        ruta_eliminada = nodo.obtenerRuta()

        # Si el directorio actual esta dentro del subarbol a eliminar,
        # retroceder el directorio actual al padre seguro.
        if self._esDescendiente(self.actual, nodo):
            self.actual = padre

        # Proceder a la eliminacion en cascada recursiva
        total_eliminados = self._eliminarEnCascadaRecursivo(nodo)

        # Desvincular del padre
        if padre is not None:
            padre.eliminarHijo(nodo)

        self.ultimo_mensaje = (
            "Elemento '%s' y sus dependencias (%d nodo(s)) eliminados correctamente."
            % (ruta_eliminada, total_eliminados)
        )

        if registrar_evento:
            registrar_evento("[ARBOL] Eliminacion en cascada: %s (%d nodos liberados)"
                             % (ruta_eliminada, total_eliminados))

        return True

    def _eliminarEnCascadaRecursivo(self, nodo):
        """Recorrido recursivo en post-orden: limpia de hojas a raiz."""
        conteo = 0
        if nodo.esCarpeta():
            # Copiamos la lista de hijos para iterar con seguridad
            hijos_a_borrar = list(nodo.hijos)
            for hijo in hijos_a_borrar:
                conteo += self._eliminarEnCascadaRecursivo(hijo)
                nodo.eliminarHijo(hijo)

        # Limpiar atributos del nodo para romper referencias circulares
        nodo.hijos.clear()
        nodo.padre = None
        conteo += 1
        return conteo

    def _esDescendiente(self, nodo, posible_ancestro):
        """Verifica si 'nodo' es igual o descendiente de 'posible_ancestro'."""
        cursor = nodo
        while cursor is not None:
            if cursor == posible_ancestro:
                return True
            cursor = cursor.padre
        return False

    # ------------------------------------------------------------------
    # 7) NAVEGACION DE DIRECTORIOS (cd / pwd)
    # ------------------------------------------------------------------
    def cambiarDirectorio(self, ruta):
        """Cambia el directorio actual de trabajo (equivalente al comando 'cd').

        Admite rutas absolutas ('/var/log'), relativas ('subcarpeta'),
        subir un nivel ('..') o volver a la raiz ('/').
        """
        nodo_destino = self.obtenerNodoPorRuta(ruta)
        if nodo_destino is None:
            self.ultimo_mensaje = "Error: El directorio '%s' no existe." % ruta
            return False

        if nodo_destino.esArchivo():
            self.ultimo_mensaje = (
                "Error: '%s' es un archivo, no un directorio." % nodo_destino.nombre
            )
            return False

        self.actual = nodo_destino
        self.ultimo_mensaje = "Directorio cambiado a '%s'." % self.actual.obtenerRuta()
        return True

    def obtenerRutaActual(self):
        """Retorna la ruta absoluta del directorio actual de trabajo (pwd)."""
        return self.actual.obtenerRuta()


# ----------------------------------------------------------------------
# PRUEBAS DEMOSTRATIVAS: se ejecutan con "python ArbolDirectorios.py"
# ----------------------------------------------------------------------
def _demo():
    print("=" * 68)
    print(" PRUEBAS DEL SISTEMA DE DIRECTORIOS (ARBOL GENERAL)")
    print("=" * 68)

    eventos = []

    def auditoria(mensaje):
        eventos.append(mensaje)

    # 1. Crear el arbol y verificar raiz '/'
    print("\n1) INICIALIZACION DEL ARBOL")
    fs = ArbolDirectorios()
    print("   Raiz creada: '%s' (tipo: %s, padre: %s)" % (
        fs.raiz.nombre, fs.raiz.tipo, fs.raiz.padre
    ))
    print("   Ruta actual de trabajo: %s" % fs.obtenerRutaActual())

    # 2. Creacion de carpetas
    print("\n2) CREACION DE CARPETAS")
    fs.crearCarpeta("bin", registrar_evento=auditoria)
    fs.crearCarpeta("etc", registrar_evento=auditoria)
    fs.crearCarpeta("home", registrar_evento=auditoria)
    fs.crearCarpeta("var", registrar_evento=auditoria)

    # Subcarpetas
    fs.crearCarpeta("usuario", destino="/home", registrar_evento=auditoria)
    fs.crearCarpeta("documentos", destino="/home/usuario", registrar_evento=auditoria)
    fs.crearCarpeta("descargas", destino="/home/usuario", registrar_evento=auditoria)
    fs.crearCarpeta("log", destino="/var", registrar_evento=auditoria)

    # Intento de duplicado
    fs.crearCarpeta("bin")
    print("   Validacion duplicado -> %s" % fs.ultimo_mensaje)

    # 3. Creacion de archivos
    print("\n3) CREACION DE ARCHIVOS")
    fs.crearArchivo("bash", destino="/bin", contenido="binario_ejecutable", registrar_evento=auditoria)
    fs.crearArchivo("network.conf", destino="/etc", contenido="IP=192.168.1.10", registrar_evento=auditoria)
    fs.crearArchivo("proyecto.py", destino="/home/usuario/documentos", contenido="print('hola')", registrar_evento=auditoria)
    fs.crearArchivo("notas.txt", destino="/home/usuario/documentos", contenido="Revisar entrega", registrar_evento=auditoria)
    fs.crearArchivo("instalador.iso", destino="/home/usuario/descargas", contenido="bytes...", registrar_evento=auditoria)
    fs.crearArchivo("syslog.log", destino="/var/log", contenido="Server started OK", registrar_evento=auditoria)

    # 4. Mostrar arbol con indentacion
    print("\n4) MOSTRAR ARBOL CON INDENTACION (Estilo Arbol Jerarquico)")
    print("-" * 68)
    fs.mostrarArbol(estilo="arbol")
    print("-" * 68)

    print("\n4.1) MOSTRAR ARBOL CON INDENTACION (Estilo Simple / Sangria)")
    print("-" * 68)
    fs.mostrarArbol(estilo="simple")
    print("-" * 68)

    # 5. Busqueda recursiva de archivos
    print("\n5) BUSQUEDA RECURSIVA DE ARCHIVOS")
    for nombre_archivo in ("proyecto.py", "syslog.log", "inexistente.txt"):
        hallado = fs.buscarArchivo(nombre_archivo)
        if hallado:
            print("   [ENCONTRADO] '%s' -> Ruta: %s (Padre: %s)" % (
                nombre_archivo, hallado.obtenerRuta(), hallado.padre.nombre
            ))
        else:
            print("   [NO EXISTE]  '%s' -> %s" % (nombre_archivo, fs.ultimo_mensaje))

    # 6. Recorrido recursivo del arbol
    print("\n6) RECORRIDO RECURSIVO DEL ARBOL (Pre-orden)")
    recorrido = []

    def visitar(nodo, nivel):
        recorrido.append("%s%s (%s)" % ("  " * nivel, nodo.nombre, nodo.tipo))

    fs.recorrerRecursivamente(funcion_visita=visitar)
    for paso in recorrido:
        print("   %s" % paso)

    # 7. Navegacion y cambio de directorio (cd)
    print("\n7) NAVEGACION DE DIRECTORIOS")
    fs.cambiarDirectorio("/home/usuario/documentos")
    print("   cd /home/usuario/documentos -> Actual: %s" % fs.obtenerRutaActual())
    fs.crearArchivo("apuntes.md", contenido="# Apuntes de clase")
    print("   Crear 'apuntes.md' en directorio actual -> %s" % fs.ultimo_mensaje)
    fs.cambiarDirectorio("..")
    print("   cd .. -> Actual: %s" % fs.obtenerRutaActual())

    # 8. Eliminacion en cascada recursiva
    print("\n8) ELIMINACION EN CASCADA RECURSIVA (Subarbol /home/usuario/descargas)")
    fs.eliminar("/home/usuario/descargas", registrar_evento=auditoria)
    print("   %s" % fs.ultimo_mensaje)

    print("\n   Arbol tras eliminar /home/usuario/descargas:")
    fs.mostrarArbol(nodo_inicio="/home", estilo="arbol")

    # 9. Eventos de auditoria registrados
    print("\n9) EVENTOS REGISTRADOS PARA AUDITORIA (network_audit_log.txt)")
    for ev in eventos:
        print("   - %s" % ev)

    print("\n" + "=" * 68)
    print(" TODAS LAS OPERACIONES Y REQUERIMIENTOS COMPLETADOS CON EXITO.")
    print("=" * 68)


if __name__ == "__main__":
    _demo()
