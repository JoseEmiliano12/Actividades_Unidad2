# Proyecto completo: grafos ponderados

Interfaz en Python con **igraph** para representar el grafo y **Tkinter** para animar las búsquedas. El grafo es no dirigido, tiene 30 nodos y 63 aristas físicas. Entre 12 y 16 hay dos aristas distintas, de pesos 16 y 3.

## Archivos

| Archivo | Función |
|---|---|
| `app.py` | Interfaz gráfica; Dijkstra, Bellman-Ford, Floyd-Warshall, BFS y DFS implementados manualmente. |
| `rutas_simples.py` | Backtracking para contar o imprimir todas las rutas sin repetir nodos. |
| `aristas.csv` | Transcripción de las 63 aristas y sus pesos. |
| `referencias/vista_previa.png` | Vista del grafo y de la ruta mínima usada como referencia visual. |
| `tests/test_algoritmos.py` | Comprobaciones de pesos, rutas y aristas paralelas. |
| `requirements.txt` | Dependencia de Python. |

## Instalación y ejecución

Desde esta carpeta:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

También puedes ejecutar `./ejecutar.sh`; el script usa `../mi_entorno` si está disponible y, en caso contrario, `.venv`.

En el equipo donde ya existe `mi_entorno`, también puedes ejecutar:

```bash
../mi_entorno/bin/python app.py
```

La interfaz abre con **nodo A = 6** y **nodo B = 44**. Puedes elegir otros dos nodos, seleccionar el algoritmo y pulsar **Preparar búsqueda**. Después usa **Atrás**, **Siguiente**, **Reproducir/Pausar** o escribe un número y pulsa **Ir al paso**. El botón **Cambiar disposición** alterna entre la distribución de la imagen y una distribución calculada por igraph.

## Algoritmos

- **Dijkstra:** menor suma de pesos; requiere pesos no negativos, como los de este grafo.
- **Bellman-Ford:** menor suma de pesos mediante relajaciones repetidas.
- **Floyd-Warshall:** calcula costos mínimos entre todos los pares. La interfaz muestra la fila del origen elegido y anima cada nodo intermedio.
- **BFS:** minimiza el número de aristas o saltos; el costo mostrado es la suma real de los pesos de su ruta, que puede no ser mínima.
- **DFS:** explora en profundidad y entrega una ruta válida; no garantiza ni costo mínimo ni menos saltos.
- **Backtracking:** genera todas las rutas simples, sin visitar dos veces el mismo nodo dentro de una ruta.

Los algoritmos de búsqueda están implementados en `app.py` y `rutas_simples.py`; no se invocan funciones de caminos mínimos o recorridos de igraph. igraph almacena los vértices, las aristas y sus atributos, y proporciona la disposición visual automática.

## Rutas simples y conteo

Para obtener solo el total sin imprimir millones de rutas:

```bash
../mi_entorno/bin/python rutas_simples.py 6 44 --solo-resumen
```

Para imprimir todas las rutas en pantalla:

```bash
../mi_entorno/bin/python rutas_simples.py 6 44
```

Para guardarlas en un archivo de texto:

```bash
../mi_entorno/bin/python rutas_simples.py 6 44 --salida todas_las_rutas.txt
```

Con origen 6 y destino 44, hay **2,869,126 rutas simples** si las aristas paralelas cuentan como rutas físicas distintas. La ruta mínima es `6 → 15 → 0 → 44`, con costo `3 + 8 + 70 = 81`. En sentido inverso, `44 → 0 → 15 → 6` también cuesta 81. **81 es un costo, no el número de rutas.**

La impresión completa produce un archivo muy grande. `--solo-resumen` recorre las mismas rutas y cuenta sin almacenar ni imprimir cada una.

## Pruebas

```bash
../mi_entorno/bin/python -m unittest discover -s tests -v
```

## Origen de los datos

`aristas.csv` y la constante `ARISTAS` de `app.py` contienen la transcripción confirmada por el usuario a partir de las imágenes del pizarrón. Las dos filas 12–16 se mantienen por separado. La imagen reconstruida usada en una etapa anterior difería del pizarrón en varios pesos; este proyecto usa la tabla corregida y confirmada.
