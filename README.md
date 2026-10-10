# Sistema de Archivos Distribuido y Enrutador de Red

**Curso:** EIF207 — Estructuras de Datos  
**Repositorio:** https://github.com/Castooor/2ProyectoEstructuras.git

## Descripción

Proyecto en Python que integra un árbol de directorios y archivos, una tabla hash para usuarios, un grafo ponderado para representar una red de servidores y un módulo de auditoría. Las funcionalidades se ejecutan desde un menú principal.

## Funcionalidades

### Árbol de directorios
- Crear carpetas y archivos.
- Buscar archivos.
- Mostrar el árbol con indentación.
- Eliminar archivos.
- Eliminar carpetas y sus dependencias de forma recursiva.
- Cambiar el directorio actual y consultar la ruta actual.

La estructura parte de la raíz `/`. Las carpetas pueden contener otros directorios y archivos; los archivos son hojas.

### Tabla hash y autenticación
- Registrar usuarios con contraseña y rol.
- Iniciar y cerrar sesión.
- Consultar el usuario activo.
- Mostrar la tabla hash y sus estadísticas.
- Demostrar colisiones.

La implementación utiliza encadenamiento para almacenar usuarios que producen el mismo índice.

### Grafo de servidores y enrutamiento
El grafo es ponderado y no dirigido: los vértices representan servidores, las aristas representan conexiones y sus pesos corresponden a la latencia en milisegundos.

- Agregar servidores.
- Agregar y eliminar conexiones.
- Consultar las conexiones de un servidor.
- Mostrar la red.
- Calcular rutas de menor latencia mediante Dijkstra.
- Comprobar conectividad mediante BFS e identificar grupos desconectados.
- Rechazar latencias negativas.

### Auditoría
Las operaciones relevantes se registran con fecha y hora en `network_audit_log.txt`. La opción de auditoría del menú principal permite consultar los registros. El archivo se genera durante la ejecución y está excluido del control de versiones mediante `.gitignore`.

## Menú principal

| Opción | Función |
|---:|---|
| 1 | Crear carpeta |
| 2 | Crear archivo |
| 3 | Buscar archivo |
| 4 | Mostrar árbol |
| 5 | Eliminar archivo |
| 6 | Eliminar carpeta |
| 7 | Cambiar directorio |
| 8 | Mostrar ruta actual |
| 9 | Registrar usuario |
| 10 | Iniciar sesión |
| 11 | Cerrar sesión |
| 12 | Mostrar usuario activo |
| 13 | Mostrar tabla hash |
| 14 | Demostrar colisiones |
| 15 | Ver auditoría |
| 16 | Red y enrutamiento |
| 0 | Salir |

El submenú de red permite agregar servidores y conexiones, eliminar conexiones, consultar conexiones, mostrar la red, calcular rutas y comprobar conectividad.

## Tecnologías y herramientas
- Python
- PyCharm
- Git y GitHub
- `unittest` para las pruebas automatizadas del árbol

## Estructura del proyecto

Módulos principales:

- `main.py`: menú principal e integración.
- `ArbolDirectorios.py`: operaciones del árbol.
- `NodoArbol.py`: nodo del árbol.
- `TablaHash.py`: tabla hash y gestión de usuarios.
- `NodoUsuario.py`: nodo utilizado por la tabla hash.
- `GrafoServidores.py`: grafo y algoritmos de red.
- `MenuGrafos.py`: submenú de red.
- `auditoria.py`: registro y consulta de auditoría.
- `test_arbol.py`: pruebas automatizadas del árbol.
- `PruebaGrafosServidores.py`: pruebas del grafo.
- `.gitignore`: archivos excluidos de Git.

## Requisitos

- Python instalado.
- Git, si se desea clonar el repositorio.
- Los archivos del proyecto en una misma carpeta.

## Instalación y ejecución

Clona el repositorio y entra en la carpeta:

```bash
git clone https://github.com/Castooor/2ProyectoEstructuras.git
cd 2ProyectoEstructuras
```

Crea un entorno virtual en Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si usas CMD en lugar de PowerShell:

```bat
.venv\Scripts\activate.bat
```

Ejecuta el sistema:

```bash
python main.py
```

También puedes ejecutar directamente el intérprete del entorno virtual desde PowerShell:

```powershell
.\.venv\Scripts\python.exe main.py
```

## Pruebas realizadas

Durante las pruebas manuales se comprobó:

- **Árbol:** creación de carpetas y archivos, búsqueda, eliminación de archivo, eliminación recursiva de una carpeta, cambio de directorio y consulta de ruta.
- **Tabla hash:** registro, inicio y cierre de sesión, consulta del usuario activo, estadísticas y colisiones con encadenamiento.
- **Grafo:** creación de servidores y conexiones, rutas de Dijkstra, cambio de ruta al eliminar una conexión y detección de una red fragmentada mediante BFS.
- **Auditoría:** registro y consulta de operaciones del árbol, usuarios y red.

Resultados de las pruebas automatizadas ejecutadas:

```text
test_arbol.py:
28 pruebas pasaron (OK).

PruebaGrafosServidores.py:
8 pruebas pasaron (OK).
```

Estos resultados corresponden a las pruebas ejecutadas durante el desarrollo; no implican que se hayan probado todas las combinaciones posibles o todos los casos límite.

Para volver a ejecutar las pruebas desde la raíz del proyecto:

```powershell
.\.venv\Scripts\python.exe -m unittest test_arbol.py
.\.venv\Scripts\python.exe PruebaGrafosServidores.py
```

## Trabajo en equipo

Distribución de responsabilidades durante el desarrollo:

- **Allison:** integración del menú principal, auditoría, coordinación con Git/GitHub y documentación.
- **Santiago:** árbol de directorios.
- **Kenan:** tabla hash y gestión de usuarios.
- **Brayan:** grafo de servidores y algoritmos de red.

## Uso de herramientas de inteligencia artificial

Durante el desarrollo se utilizó ChatGPT como apoyo para planificar la integración, aclarar conceptos, organizar pruebas manuales y automatizadas, interpretar resultados y preparar documentación. La herramienta se usó como apoyo; el equipo ejecutó el programa y comprobó los resultados.

Ejemplos representativos de solicitudes realizadas:

- “Ayúdame a integrar el menú de grafos con el menú principal y la auditoría sin reemplazar las partes existentes”.
- “Guíame paso a paso para probar la creación, búsqueda y eliminación de archivos desde el menú”.
- “Ayúdame a interpretar la salida de las pruebas automatizadas y documentar los resultados”.
- "Explicame como funciona una tabla hash" (Esto antes de la explicacion en clase).

Las sugerencias se revisaron de acuerdo con el código y los resultados obtenidos. El equipo debe poder explicar las estructuras de datos, los algoritmos y las decisiones de implementación durante la defensa.

## Control de versiones

El proyecto se trabajó con Git y GitHub, utilizando la rama `Allison` para integrar y probar los módulos. El historial de commits permite consultar los cambios realizados durante el desarrollo.

## Observaciones

- `network_audit_log.txt` se genera durante la ejecución y no se versiona.
- Las pruebas documentadas son las ejecutadas durante el desarrollo.
- Antes de la entrega definitiva, el equipo debe confirmar que la rama entregada contiene todos los cambios esperados y que cada integrante puede explicar su parte.
