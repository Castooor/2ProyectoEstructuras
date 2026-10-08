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

    def __init__(self, tamano=TAMANO_TABLA):
        if not isinstance(tamano, int) or tamano <= 0:
            raise ValueError("El tamano de la tabla debe ser un entero positivo.")
        self.tamano = tamano
        self.tabla = [None] * self.tamano
        self.total_usuarios = 0
        self.intentosFallidos = 0
        self.ultimo_mensaje = ""
        self._usuario_activo = None

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

        Lanza ValueError si el nombre o la contrasena estan vacios.
        """
        clave = self._clave(nombre)
        if clave == "":
            raise ValueError("El nombre de usuario no puede estar vacio.")
        if contrasena is None or str(contrasena) == "":
            raise ValueError("La contrasena no puede estar vacia.")

        rol = str(rol).strip().lower()
        if rol not in ROLES_VALIDOS:
            raise ValueError("El rol '%s' no es valido. Debe ser: %s" % (rol, ", ".join(ROLES_VALIDOS)))

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
    # 3.1) PERMISOS POR ROL (los consume el modulo de directorios y el menu de integracion)
    # ------------------------------------------------------------------

    def esAdministrador(self):
        """True si el usuario activo tiene rol de administrador."""
        return self._usuario_activo is not None and self._usuario_activo.rol == ROL_ADMINISTRADOR

    def verificarPermiso(self, accion, registrar_evento=None):
        """Verifica si el usuario activo puede ejecutar la accion solicitada.

        Las acciones sensibles (crear/eliminar carpetas, cambiar permisos,
        etc) solo las puede ejecutar un administrador; el resto de acciones
        son validas para cualquier usuario.
        """
        if self.esAdministrador():
            return True
        if self._usuario_activo is None:
            self.ultimo_mensaje = "No hay sesion activa; no se puede ejecutar '%s'." % accion
            return False
        else: 
            self.ultimo_mensaje = "El usuario '%s' no tiene permiso para ejecutar '%s'." % (self._usuario_activo.nombre, accion)
            self._notificar(registrar_evento, "Acceso denegado a: %s" % accion, self._usuario_activo.nombre)
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

    def _nombresQueColisionan(self, tabla, nombre_base, cantidad=3, limite=20000):
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