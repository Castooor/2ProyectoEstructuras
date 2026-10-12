# -*- coding: utf-8 -*-
"""
Tabla hash implementada desde cero (sin librerias externas y sin usar
diccionarios de Python) para validar las credenciales de los usuarios en
tiempo constante promedio O(1), tal como lo exige el enunciado del proyecto.

Decisiones de diseno
--------------------
* Tamano fijo de la tabla: 50 indices (0 .. 49).
* Funcion hash propia (metodos 'codigoHash' y 'funcionHash'): recibe el
  nombre de usuario (string) y devuelve el indice donde vive su credencial.
* Resolucion de colisiones: ENCADENAMIENTO. Cada indice guarda la cabeza de
  una LISTA SIMPLE de nodos 'NodoUsuario' enlazados con el atributo
  'siguiente'; los usuarios que caen en el mismo indice se agregan al inicio
  de esa cadena.
* Ningun metodo recorre la tabla completa para autenticar: se calcula el
  indice con la funcion hash y se camina unicamente la cadena de ese indice
  (promedio O(1 + alfa), donde alfa es el factor de carga).

Uso basico desde el menu de integracion
---------------------------------------
    from TablaHash import TablaHash

    auth = TablaHash()
    auth.registrarUsuario("kenan", "Kenan123", rol="administrador")
    if auth.iniciarSesion("kenan", "Kenan123"):
        print(auth.usuarioActivo.nombre, auth.usuarioActivo.rol)
"""

# La entidad NodoUsuario vive en su propio archivo (responsabilidad unica, SRP);
# TablaHash importa la clase para poder construir las cadenas de cada indice.
import json
import os

from NodoUsuario import NodoUsuario

# Tamano de la tabla hash: 50 posiciones o "buckets".
TAMANO_TABLA = 50

# Roles permitidos en el sistema. Las acciones sensibles (por ejemplo crear o
# eliminar carpetas en el arbol de directorios) solo las puede ejecutar un
# usuario con rol de administrador; ver 'esAdministrador' y 'verificarPermiso'.
ROL_USUARIO = "usuario"
ROL_ADMINISTRADOR = "administrador"
ROLES_VALIDOS = (ROL_USUARIO, ROL_ADMINISTRADOR)


class TablaHash:
    """Tabla hash de usuarios (tamano 50) con encadenamiento por listas simples.

    La tabla es un arreglo de 50 "punteros": 'self.tabla[i]' es la cabeza de
    la lista simple de usuarios cuyo nombre produce el indice i. Si el indice
    esta libre el valor es None (cadena vacia).
    """

    def __init__(self, tamano=TAMANO_TABLA, archivo=None):
        if not isinstance(tamano, int) or tamano <= 0:
            raise ValueError("El tamano de la tabla debe ser un entero positivo.")
        self.tamano = tamano
        self.tabla = [None] * self.tamano
        self.total_usuarios = 0
        self.intentosFallidos = 0
        self.ultimo_mensaje = ""
        self._usuario_activo = None
        # Persistencia: si se indica un archivo JSON, los usuarios se cargan al
        # crear la tabla y se guardan solos tras cada registro/eliminacion.
        self.archivo = archivo
        self.ultimo_error = ""      # ultimo problema de persistencia ("" si no hubo)
        self._cargando = False
        if self.archivo:
            self.cargar()

    # ------------------------------------------------------------------
    # 0) PERSISTENCIA (archivo JSON)
    # ------------------------------------------------------------------
    def guardar(self):
        """Escribe todos los usuarios en el archivo JSON (si hay archivo).

        Nunca lanza excepciones: devuelve True si guardo (o si no hay archivo)
        y False si fallo; en ese caso el motivo queda en 'ultimo_error'.
        Se escribe primero a un temporal y luego se reemplaza, para que un
        corte a mitad de escritura no deje el archivo de usuarios a medias.
        """
        if not self.archivo or self._cargando:
            return True
        temporal = self.archivo + ".tmp"
        try:
            usuarios = []
            for indice in range(self.tamano):
                cadena = []
                actual = self.tabla[indice]
                while actual is not None:
                    cadena.append({"nombre": actual.nombre,
                                   "contrasena": actual.contrasena,
                                   "rol": actual.rol})
                    actual = actual.siguiente
                # Se guarda al reves: al recargar cada usuario se enlaza al
                # inicio de su cadena, asi el orden original se conserva.
                usuarios.extend(reversed(cadena))
            with open(temporal, "w", encoding="utf-8") as f:
                json.dump({"usuarios": usuarios}, f, ensure_ascii=False,
                          indent=2, allow_nan=False)
            os.replace(temporal, self.archivo)
        except (OSError, ValueError, TypeError) as error:
            self.ultimo_error = "No se pudo guardar '%s': %s" % (self.archivo, error)
            try:
                os.remove(temporal)
            except OSError:
                pass
            return False
        self.ultimo_error = ""
        return True

    def _guardar_y_avisar(self, registrar_evento):
        """Guarda en disco; si falla, lo deja en la auditoria y devuelve un
        texto de advertencia para el mensaje que ve el usuario."""
        if self.guardar():
            return ""
        self._notificar(registrar_evento, "ERROR de persistencia: %s" % self.ultimo_error)
        return " ADVERTENCIA: no se pudo guardar en disco."

    def _respaldar_corrupto(self):
        """Aparta el archivo danado como '<archivo>.corrupto' (sin lanzar errores)."""
        try:
            os.replace(self.archivo, self.archivo + ".corrupto")
        except OSError:
            pass

    def cargar(self):
        """Lee el archivo JSON y reconstruye la tabla hash con sus cadenas.

        Si el archivo no existe no hace nada (primera ejecucion). Si esta
        danado, lo respalda como '<archivo>.corrupto' y arranca vacia dejando
        el motivo en 'ultimo_error'. Nunca lanza excepciones.
        Devuelve la cantidad de usuarios cargados.
        """
        if not self.archivo or not os.path.exists(self.archivo):
            return 0
        try:
            with open(self.archivo, "r", encoding="utf-8") as f:
                datos = json.load(f)
            registros = datos["usuarios"]
            self._cargando = True
            for r in registros:
                self.registrarUsuario(r["nombre"], r["contrasena"], r["rol"])
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            self._cargando = False
            self.tabla = [None] * self.tamano
            self.total_usuarios = 0
            self._respaldar_corrupto()
            self.ultimo_error = ("Archivo de usuarios '%s' danado o ilegible; "
                                 "se respaldo como .corrupto y se inicio vacio." % self.archivo)
            self.ultimo_mensaje = self.ultimo_error
            return 0
        finally:
            self._cargando = False
        self.ultimo_mensaje = "Usuarios cargados desde '%s'." % self.archivo
        return self.total_usuarios

    # ------------------------------------------------------------------
    # 1) FUNCION HASH: convierte el nombre de usuario en un indice valido
    # ------------------------------------------------------------------
    @staticmethod
    def _clave(nombre):
        """Normaliza la clave: sin espacios externos y en minusculas.

        Asi 'Kenan' y ' kenan ' apuntan al mismo usuario y al mismo indice.
        """
        return str(nombre).strip().lower()

    def codigoHash(self, nombre):
        """Codigo de dispersion del nombre, SIN aplicar todavia el modulo.

        Es el metodo de Horner con base 31:

            codigo = 0
            para cada caracter c: codigo = codigo * 31 + ord(c)

        Al multiplicar el acumulado por 31 y sumarle el codigo ASCII del
        caracter, el resultado depende del valor Y del orden de las letras,
        por lo que dos nombres diferentes producen codigos diferentes (y
        nombres iguales producen siempre el mismo codigo).
        """
        clave = self._clave(nombre)
        if clave == "":
            raise ValueError("El nombre de usuario no puede estar vacio.")
        codigo = 0
        for caracter in clave:
            codigo = codigo * 31 + ord(caracter)
        return codigo

    def funcionHash(self, nombre):
        """Devuelve el indice de la tabla para un nombre: 0 <= indice < tamano.

            indice = codigoHash(nombre) % tamano

        El modulo garantiza que el indice siempre caiga dentro del arreglo;
        los nombres cuyo codigo comparte el mismo resto producen una colision
        que se resuelve con la cadena de ese indice.
        """
        return self.codigoHash(nombre) % self.tamano

    # ------------------------------------------------------------------
    # 2) BUSQUEDA INTERNA (recorre solamente la cadena del indice)
    # ------------------------------------------------------------------
    def _buscarNodo(self, nombre):
        """Devuelve la tupla (nodo, anterior, indice).

        'nodo' es None si el usuario no existe. 'anterior' es el nodo que lo
        precede dentro de la cadena (None si es la cabeza): ese dato es el que
        permite reconectar los enlaces al eliminar.
        """
        indice = self.funcionHash(nombre)
        clave = self._clave(nombre)
        anterior = None
        actual = self.tabla[indice]
        while actual is not None:
            if self._clave(actual.nombre) == clave:
                return actual, anterior, indice
            anterior = actual
            actual = actual.siguiente
        return None, None, indice

    # ------------------------------------------------------------------
    # 3) AUTENTICACION: registrar, buscar, validar e iniciar sesion
    # ------------------------------------------------------------------
    @staticmethod
    def _notificar(registrar_evento, mensaje):
        """Invoca el callback de auditoria unicamente si fue proporcionado.

        Permite conectar este modulo con la clase de Auditoria (Allison) sin
        acoplar la tabla hash a la escritura de archivos: la tabla solo avisa
        de los eventos, quien decide que hacer con ellos es el modulo externo.
        """
        if callable(registrar_evento):
            registrar_evento(mensaje)

    def registrarUsuario(self, nombre, contrasena, rol="usuario", registrar_evento=None):
        """Inserta un usuario nuevo en la tabla hash.

        Se enlaza al inicio de la cadena del indice calculado por
        'funcionHash', por lo que la operacion es O(1) en el caso promedio.

        Devuelve:
            True  -> el usuario se registro correctamente.
            False -> el nombre ya estaba registrado.

        Lanza ValueError si el nombre o la contrasena estan vacios, o si el
        rol no es 'usuario' ni 'administrador'.
        """
        clave = self._clave(nombre)
        if clave == "":
            raise ValueError("El nombre de usuario no puede estar vacio.")
        if contrasena is None or str(contrasena) == "":
            raise ValueError("La contrasena no puede estar vacia.")
        rol = str(rol).strip().lower()
        if rol not in ROLES_VALIDOS:
            raise ValueError("Rol invalido '%s'. Use: %s." % (rol, " o ".join(ROLES_VALIDOS)))

        nodo, _, indice = self._buscarNodo(nombre)
        if nodo is not None:
            self.ultimo_mensaje = "El usuario '%s' ya existe (indice %d)." % (nombre, indice)
            return False

        nuevo = NodoUsuario(str(nombre).strip(), str(contrasena), rol)
        nuevo.siguiente = self.tabla[indice]   # encadenamiento: se enlaza la cabeza anterior
        self.tabla[indice] = nuevo
        self.total_usuarios += 1
        self.ultimo_mensaje = "Usuario '%s' registrado en el indice %d." % (nuevo.nombre, indice)
        self._notificar(registrar_evento,
                        "Registro de usuario: %s (rol %s)" % (nuevo.nombre, nuevo.rol))
        self.ultimo_mensaje += self._guardar_y_avisar(registrar_evento)
        return True

    def buscarUsuario(self, nombre):
        """Devuelve el NodoUsuario del nombre indicado, o None si no existe.

        No recorre la tabla ni una lista secuencial: calcula el indice con la
        funcion hash y recorre unicamente la cadena de ese indice.
        """
        if self._clave(nombre) == "":
            return None
        nodo, _, _ = self._buscarNodo(nombre)
        return nodo

    def validarCredenciales(self, nombre, contrasena):
        """Verifica usuario y contrasena. Devuelve True solo si ambos coinciden.

        Por seguridad no revela cual de los dos datos fallo. Es O(1) promedio,
        porque ubicar al usuario no depende de un recorrido secuencial de
        todos los usuarios del sistema.
        """
        nodo = self.buscarUsuario(nombre)
        if nodo is None or contrasena is None:
            return False
        return nodo.contrasena == str(contrasena)

    def iniciarSesion(self, nombre, contrasena, registrar_evento=None):
        """Valida las credenciales y abre la sesion del usuario.

        Si el inicio de sesion es correcto, 'usuarioActivo' queda apuntando al
        nodo del usuario para que el resto del sistema (menu, archivos, red)
        sepa quien esta operando. Devuelve True si el login fue exitoso.
        """
        if self.validarCredenciales(nombre, contrasena):
            self._usuario_activo = self.buscarUsuario(nombre)
            self.ultimo_mensaje = "Sesion iniciada por '%s'." % self._usuario_activo.nombre
            self._notificar(registrar_evento,
                            "Inicio de sesion exitoso: %s" % self._usuario_activo.nombre)
            return True

        self._usuario_activo = None
        self.intentosFallidos += 1
        if self.buscarUsuario(nombre) is None:
            self.ultimo_mensaje = "El usuario '%s' no existe." % nombre
            motivo = "usuario inexistente"
        else:
            self.ultimo_mensaje = "Contrasena incorrecta para '%s'." % nombre
            motivo = "contrasena incorrecta"
        self._notificar(registrar_evento,
                        "Inicio de sesion fallido (%s): %s" % (motivo, nombre))
        return False

    def cerrarSesion(self, registrar_evento=None):
        """Cierra la sesion activa y devuelve el nombre del usuario, o None."""
        if self._usuario_activo is None:
            return None
        nombre = self._usuario_activo.nombre
        self._usuario_activo = None
        self.ultimo_mensaje = "Sesion cerrada: '%s'." % nombre
        self._notificar(registrar_evento, "Cierre de sesion: %s" % nombre)
        return nombre

    @property
    def usuarioActivo(self):
        """Nodo del usuario con sesion abierta (None si nadie ha iniciado sesion)."""
        return self._usuario_activo

    def haySesionActiva(self):
        """True si existe una sesion abierta."""
        return self._usuario_activo is not None

    # ------------------------------------------------------------------
    # 3b) PERMISOS POR ROL (los consume el modulo de directorios)
    # ------------------------------------------------------------------
    def esAdministrador(self):
        """True solo si hay una sesion abierta y su rol es 'administrador'."""
        return (self._usuario_activo is not None
                and self._usuario_activo.rol == ROL_ADMINISTRADOR)

    def verificarPermiso(self, accion, registrar_evento=None):
        """Autoriza una accion restringida a administradores.

        Uso desde otro modulo, antes de crear o eliminar carpetas/archivos:

            if not auth.verificarPermiso("eliminar carpeta /docs", registrar_evento=log):
                return          # acceso denegado; 'ultimo_mensaje' dice por que

        Devuelve True si el usuario activo es administrador. Si no hay sesion
        o el rol es 'usuario', devuelve False, deja el motivo en
        'ultimo_mensaje' y avisa al callback de auditoria del intento denegado.
        """
        if self.esAdministrador():
            return True
        if self._usuario_activo is None:
            quien = "sin sesion activa"
        else:
            quien = "%s (rol %s)" % (self._usuario_activo.nombre, self._usuario_activo.rol)
        self.ultimo_mensaje = "Acceso denegado: '%s' requiere rol administrador." % accion
        self._notificar(registrar_evento,
                        "Acceso denegado a '%s': %s" % (accion, quien))
        return False

    # ------------------------------------------------------------------
    # 4) ELIMINACION (reconecta los enlaces de la lista simple)
    # ------------------------------------------------------------------
    def eliminarUsuario(self, nombre, registrar_evento=None):
        """Elimina al usuario de la tabla y libera su nodo.

        Casos de enlace dentro de la cadena:
          * El nodo es la CABEZA: el indice pasa a apuntar a nodo.siguiente.
          * El nodo esta EN MEDIO o al final: el nodo anterior salta por encima
            (anterior.siguiente = nodo.siguiente), de modo que nunca queda un
            nodo huerfano ni una cadena rota.

        Si el usuario eliminado tenia la sesion abierta, esta se cierra.
        Devuelve True si el usuario existia y se elimino; False si no existia.
        """
        if self._clave(nombre) == "":
            return False

        nodo, anterior, indice = self._buscarNodo(nombre)
        if nodo is None:
            self.ultimo_mensaje = "No existe el usuario '%s'." % nombre
            return False

        if anterior is None:
            self.tabla[indice] = nodo.siguiente
        else:
            anterior.siguiente = nodo.siguiente

        nodo.siguiente = None              # se suelta el enlace del nodo eliminado
        self.total_usuarios -= 1
        if self._usuario_activo is nodo:   # si era el usuario conectado, se cierra su sesion
            self._usuario_activo = None
        self.ultimo_mensaje = "Usuario '%s' eliminado del indice %d." % (nodo.nombre, indice)
        self._notificar(registrar_evento, "Eliminacion de usuario: %s" % nodo.nombre)
        self.ultimo_mensaje += self._guardar_y_avisar(registrar_evento)
        return True

    # ------------------------------------------------------------------
    # 5) UTILITARIAS DE CONSULTA Y PRUEBAS
    # ------------------------------------------------------------------
    def obtenerCadena(self, indice):
        """Devuelve la lista de nombres que forman la cadena de un indice."""
        if not 0 <= indice < self.tamano:
            raise IndexError("Indice fuera del rango 0..%d." % (self.tamano - 1))
        nombres = []
        actual = self.tabla[indice]
        while actual is not None:
            nombres.append(actual.nombre)
            actual = actual.siguiente
        return nombres

    def estadisticas(self):
        """Resumen del estado de la tabla: ocupacion, colisiones y carga.

        'colisiones' se calcula en vivo como usuarios - indices ocupados, es
        decir los usuarios que llegaron a un indice que ya tenia alguien (los
        que quedaron dentro de una cadena en lugar de ser la cabeza).
        """
        ocupados = 0
        cadena_mas_larga = 0
        for indice in range(self.tamano):
            actual = self.tabla[indice]
            if actual is None:
                continue
            ocupados += 1
            largo = 0
            while actual is not None:
                largo += 1
                actual = actual.siguiente
            if largo > cadena_mas_larga:
                cadena_mas_larga = largo
        return {
            "tamano": self.tamano,
            "usuarios": self.total_usuarios,
            "indices_ocupados": ocupados,
            "indices_libres": self.tamano - ocupados,
            "colisiones": self.total_usuarios - ocupados,
            "cadena_mas_larga": cadena_mas_larga,
            "factor_carga": round(self.total_usuarios / self.tamano, 4),
            "intentos_fallidos": self.intentosFallidos,
        }

    def mostrarTabla(self):
        """Imprime en consola los indices ocupados y sus cadenas de colisiones."""
        print("-" * 64)
        print("TABLA HASH DE USUARIOS (encadenamiento con listas simples)")
        print("-" * 64)
        if self.total_usuarios == 0:
            print("  La tabla esta vacia.")
        for indice in range(self.tamano):
            if self.tabla[indice] is None:
                continue
            nombres = self.obtenerCadena(indice)
            etiqueta = "   <-- COLISION: %d usuarios" % len(nombres) if len(nombres) > 1 else ""
            print("  [%2d] %s%s" % (indice, " -> ".join(nombres), etiqueta))
        datos = self.estadisticas()
        print("-" * 64)
        print("  Usuarios: %d | indices ocupados: %d de %d | colisiones: %d" %
              (datos["usuarios"], datos["indices_ocupados"], datos["tamano"], datos["colisiones"]))
        print("  Factor de carga: %.4f | cadena mas larga: %d | intentos fallidos: %d" %
              (datos["factor_carga"], datos["cadena_mas_larga"], datos["intentos_fallidos"]))
        print("-" * 64)

    def __len__(self):
        """Cantidad de usuarios registrados."""
        return self.total_usuarios

    def __contains__(self, nombre):
        """Permite escribir: 'kenan' in tabla"""
        return self.buscarUsuario(nombre) is not None


# ----------------------------------------------------------------------
# PRUEBAS MANUALES: se ejecutan solo con "python TablaHash.py"
# ----------------------------------------------------------------------
def _nombresQueColisionan(tabla, nombre_base, cantidad=3, limite=20000):
    """Busca nombres que producen el mismo indice que 'nombre_base'.

    Devuelve (indice, [nombres]). Se generan candidatos con un contador y se
    conserva la funcion hash intacta: son colisiones reales, no simuladas.
    """
    indice = tabla.funcionHash(nombre_base)
    encontrados = []
    contador = 1
    while len(encontrados) < cantidad and contador <= limite:
        candidato = "%s%d" % (nombre_base, contador)
        if tabla.funcionHash(candidato) == indice:
            encontrados.append(candidato)
        contador += 1
    return indice, encontrados


def _demo():
    print("=" * 64)
    print(" PRUEBAS DEL MODULO HASH / AUTENTICACION")
    print("=" * 64)

    eventos = []

    def auditoria(mensaje):
        eventos.append(mensaje)

    auth = TablaHash()
    print("Tamano de la tabla: %d indices (0 .. %d)\n" % (auth.tamano, auth.tamano - 1))

    print("1) FUNCION HASH: nombre -> codigo -> indice")
    for nombre in ("santiago", "brayan", "kenan", "allison"):
        print("   %-9s codigoHash=%-24d funcionHash=%2d" %
              (nombre, auth.codigoHash(nombre), auth.funcionHash(nombre)))

    print("\n2) REGISTRO DE USUARIOS")
    registros = [
        ("santiago", "Santi2026", "administrador"),
        ("Brayan", "Brayan123", "usuario"),
        ("kenan", "Kenan123", "administrador"),
        ("allison", "Allison123", "usuario"),
    ]
    for nombre, contrasena, rol in registros:
        ok = auth.registrarUsuario(nombre, contrasena, rol, registrar_evento=auditoria)
        print("   [%-5s] %s" % ("OK" if ok else "ERROR", auth.ultimo_mensaje))
    print("   Repetido -> registrarUsuario('KENAN', 'OtraClave') = %s" %
          auth.registrarUsuario("KENAN", "OtraClave"))
    print("   Total de usuarios registrados: %d" % len(auth))

    print("\n3) INICIAR SESION Y VALIDAR CREDENCIALES")
    casos = [
        ("kenan", "Kenan123", True),
        ("kenan", "claveMala", False),
        ("  SANTIAGO  ", "Santi2026", True),
        ("usuarioFantasma", "1234", False),
        ("allison", "", False),
    ]
    for nombre, contrasena, esperado in casos:
        resultado = auth.iniciarSesion(nombre, contrasena, registrar_evento=auditoria)
        marca = "OK" if resultado == esperado else "REVISAR"
        print("   [%-7s] iniciarSesion('-%s-', '-%s-') = %-5s | %s" %
              (marca, nombre, contrasena, resultado, auth.ultimo_mensaje))
        auth.cerrarSesion()

    print("\n4) USUARIO AUTENTICADO (lo que consume el menu)")
    auth.iniciarSesion("kenan", "Kenan123", registrar_evento=auditoria)
    if auth.haySesionActiva():
        print("   Sesion activa: %s (rol %s)" %
              (auth.usuarioActivo.nombre, auth.usuarioActivo.rol))
    print("   cerrarSesion() = %s | hay sesion activa? %s" %
          (auth.cerrarSesion(registrar_evento=auditoria), auth.haySesionActiva()))

    print("\n4b) PERMISOS POR ROL (solo el administrador puede acciones restringidas)")
    print("   Sin sesion  -> verificarPermiso = %s | %s" %
          (auth.verificarPermiso("eliminar carpeta", registrar_evento=auditoria), auth.ultimo_mensaje))
    auth.iniciarSesion("allison", "Allison123", registrar_evento=auditoria)
    print("   allison (usuario)       -> %s | %s" %
          (auth.verificarPermiso("eliminar carpeta", registrar_evento=auditoria), auth.ultimo_mensaje))
    auth.iniciarSesion("kenan", "Kenan123", registrar_evento=auditoria)
    print("   kenan (administrador)   -> %s" %
          auth.verificarPermiso("eliminar carpeta", registrar_evento=auditoria))
    auth.cerrarSesion()
    try:
        auth.registrarUsuario("intruso", "x123", "superroot")
    except ValueError as error:
        print("   Rol invalido rechazado: %s" % error)

    print("\n5) COLISIONES Y SU RESOLUCION POR ENCADENAMIENTO")
    indice, colisionados = _nombresQueColisionan(auth, "santiago", 3)
    print("   'santiago' vive en el indice %d; estos nombres llegan al mismo indice:" % indice)
    for nombre in colisionados:
        auth.registrarUsuario(nombre, "clave123", registrar_evento=auditoria)
        print("      %-12s -> indice %d" % (nombre, auth.funcionHash(nombre)))
    print("   Cadena del indice %d: %s" % (indice, " -> ".join(auth.obtenerCadena(indice))))
    if colisionados:
        print("   Login de un usuario que colisiono: %s | %s" %
              (auth.iniciarSesion(colisionados[0], "clave123"), auth.ultimo_mensaje))
        auth.cerrarSesion()

    print("\n6) ELIMINAR USUARIO (reconexion de enlaces)")
    for nombre in ("brayan", "brayan", "santiago"):
        resultado = auth.eliminarUsuario(nombre, registrar_evento=auditoria)
        print("   eliminarUsuario('%-9s') = %-5s | %s" % (nombre, resultado, auth.ultimo_mensaje))
    print("   Cadena del indice %d tras eliminar: %s" %
          (indice, " -> ".join(auth.obtenerCadena(indice))))
    print("   buscarUsuario('santiago') (eliminado) = %s" % auth.buscarUsuario("santiago"))
    print("   Login de usuario eliminado: %s | %s" %
          (auth.iniciarSesion("brayan", "Brayan123"), auth.ultimo_mensaje))

    print("\n7) ESTADO FINAL DE LA TABLA")
    auth.mostrarTabla()

    print("\n8) EVENTOS ENVIADOS AL CALLBACK DE AUDITORIA")
    for mensaje in eventos:
        print("   - %s" % mensaje)

    print("\nFin de las pruebas. El menu puede importar: from TablaHash import TablaHash")


if __name__ == "__main__":
    _demo()