"""Visualizador de un multigrafo ponderado con búsquedas animadas.

Requisitos: Python 3, tkinter y python-igraph.
Instalación: python -m pip install igraph

igraph almacena y organiza el grafo. Dijkstra, Bellman-Ford, BFS y DFS están
implementados aquí, sin llamar a funciones de búsqueda de igraph.
"""

from dataclasses import dataclass
import math
import tkinter as tk
from tkinter import messagebox, ttk

import igraph as ig


# Transcripción confirmada del pizarrón. Cada tupla es una arista física.
# (12, 16, 16) y (12, 16, 3) son paralelas y deben conservarse.
ARISTAS = [
    (0, 1, 2), (0, 15, 8), (0, 44, 70),
    (1, 2, 3), (1, 7, 20), (1, 8, 7), (1, 10, 5),
    (1, 12, 7), (1, 15, 8), (1, 23, 7),
    (2, 3, 9), (2, 17, 5), (2, 23, 3), (2, 69, 11),
    (3, 5, 2), (3, 44, 80), (3, 69, 6),
    (4, 8, 15), (4, 10, 6), (4, 14, 8), (4, 18, 5), (4, 27, 3),
    (5, 20, 2), (5, 44, 69), (5, 69, 3),
    (6, 7, 10), (6, 8, 4), (6, 9, 7), (6, 14, 5), (6, 15, 3),
    (7, 11, 5), (7, 14, 3), (7, 29, 5),
    (8, 12, 9), (8, 15, 2),
    (9, 10, 3), (9, 14, 5),
    (10, 11, 7), (10, 14, 9), (10, 27, 9),
    (11, 14, 9), (11, 21, 2), (11, 24, 7),
    (12, 13, 9), (12, 16, 16), (12, 16, 3),
    (12, 18, 4), (12, 66, 7),
    (13, 16, 3), (13, 66, 777),
    (16, 17, 7), (16, 23, 11),
    (17, 69, 4), (17, 70, 6),
    (18, 66, 6),
    (20, 25, 7), (20, 69, 3),
    (21, 24, 2), (21, 29, 3),
    (25, 69, 6), (25, 70, 17),
    (27, 66, 1), (69, 70, 8),
]

# Coordenadas que mantienen la disposición de la imagen original.
POSICIONES = {
    29: (145, 135), 21: (145, 285), 24: (145, 520),
    7: (345, 135), 11: (290, 400), 14: (415, 405),
    10: (420, 585), 27: (395, 745), 4: (585, 720),
    18: (680, 720), 66: (780, 860), 13: (945, 855),
    6: (575, 285), 9: (575, 405), 8: (705, 440),
    12: (830, 605), 15: (805, 285), 0: (985, 180),
    1: (985, 440), 23: (1035, 555), 16: (1040, 740),
    44: (1130, 130), 3: (1130, 285), 2: (1130, 440),
    17: (1170, 625), 5: (1300, 245), 69: (1300, 440),
    20: (1455, 330), 25: (1455, 520), 70: (1385, 680),
}


def construir_grafo():
    """Crea en igraph un grafo no dirigido, ponderado y con aristas paralelas."""
    nombres = sorted({n for a, b, _ in ARISTAS for n in (a, b)})
    indice = {nombre: i for i, nombre in enumerate(nombres)}
    pares = [(indice[a], indice[b]) for a, b, _ in ARISTAS]
    grafo = ig.Graph(n=len(nombres), edges=pares, directed=False)
    grafo.vs["nombre"] = nombres
    grafo.es["peso"] = [peso for _, _, peso in ARISTAS]
    # igraph.Layout aporta las coordenadas; Tkinter las dibuja y anima.
    disposicion = ig.Layout([POSICIONES[nombre] for nombre in nombres])
    return grafo, indice, disposicion


def construir_matriz(grafo):
    """Matriz de adyacencia; cada celda guarda todas sus aristas físicas.

    Se construye recorriendo igraph.es. Así la pareja 12–16 conserva ambos
    pesos y cada arista tiene un identificador visual propio.
    """
    n = grafo.vcount()
    matriz = [[[] for _ in range(n)] for _ in range(n)]
    for arista in grafo.es:
        u, v = arista.tuple
        peso = int(arista["peso"])
        matriz[u][v].append((arista.index, peso))
        matriz[v][u].append((arista.index, peso))
    return matriz


@dataclass
class Paso:
    mensaje: str
    actual: int | None
    arista: int | None
    visitados: frozenset
    frontera: tuple
    distancias: tuple
    predecesores: tuple
    aristas_previas: tuple
    terminado: bool = False
    ruta: tuple = ()
    ruta_aristas: tuple = ()
    costo: int | None = None


def guardar(pasos, mensaje, actual, arista, visitados, frontera, dist, pred,
            pred_arista, terminado=False, ruta=(), ruta_aristas=(), costo=None):
    """Guarda una copia del estado para avanzar o retroceder sin recalcular."""
    pasos.append(Paso(mensaje, actual, arista, frozenset(visitados),
                      tuple(frontera), tuple(dist), tuple(pred),
                      tuple(pred_arista), terminado, tuple(ruta),
                      tuple(ruta_aristas), costo))


def reconstruir_ruta(grafo, origen, destino, pred, pred_arista):
    """Reconstruye nodos y aristas elegidas, respetando las paralelas."""
    nodos = []
    aristas = []
    actual = destino
    vistos = set()
    while actual != -1 and actual not in vistos:
        vistos.add(actual)
        nodos.append(actual)
        if actual == origen:
            break
        if pred_arista[actual] == -1:
            break
        aristas.append(pred_arista[actual])
        actual = pred[actual]
    if not nodos or nodos[-1] != origen:
        return (), (), None
    nodos.reverse()
    aristas.reverse()
    costo = sum(int(grafo.es[eid]["peso"]) for eid in aristas)
    return tuple(nodos), tuple(aristas), costo


def dijkstra_manual(grafo, matriz, origen, destino):
    """Dijkstra O(V²+E), sin shortest_paths ni otra búsqueda prefabricada."""
    n = grafo.vcount()
    inf = float("inf")
    dist = [inf] * n
    pred = [-1] * n
    pred_arista = [-1] * n
    visitados = set()
    dist[origen] = 0
    pasos = []
    guardar(pasos, "Inicio: la distancia del origen es 0.", None, None,
            visitados, [origen], dist, pred, pred_arista)

    for _ in range(n):
        u = -1
        for i in range(n):
            if i not in visitados and dist[i] != inf:
                if u == -1 or dist[i] < dist[u]:
                    u = i
        if u == -1:
            break
        visitados.add(u)
        nombre = grafo.vs[u]["nombre"]
        frontera = [i for i in range(n) if i not in visitados and dist[i] != inf]
        guardar(pasos, f"Se selecciona {nombre}: costo definitivo {dist[u]}.",
                u, None, visitados, frontera, dist, pred, pred_arista)
        if u == destino:
            break
        for v in range(n):
            if v in visitados:
                continue
            for eid, peso in matriz[u][v]:
                candidato = dist[u] + peso
                if candidato < dist[v]:
                    dist[v] = candidato
                    pred[v] = u
                    pred_arista[v] = eid
                    frontera = [i for i in range(n)
                                if i not in visitados and dist[i] != inf]
                    guardar(pasos,
                            f"{nombre} → {grafo.vs[v]['nombre']}: "
                            f"{dist[u]} + {peso} = {candidato}; se mejora la distancia.",
                            u, eid, visitados, frontera, dist, pred, pred_arista)

    ruta, ruta_aristas, costo = reconstruir_ruta(
        grafo, origen, destino, pred, pred_arista)
    mensaje = (f"Terminado: costo mínimo {costo}." if ruta
               else "Terminado: no hay ruta entre esos nodos.")
    guardar(pasos, mensaje, destino if ruta else None, None, visitados, (),
            dist, pred, pred_arista, True, ruta, ruta_aristas, costo)
    return pasos


def bellman_ford_manual(grafo, _matriz, origen, destino):
    """Relaja cada arista en ambos sentidos; no usa Bellman-Ford de igraph."""
    n = grafo.vcount()
    inf = float("inf")
    dist = [inf] * n
    pred = [-1] * n
    pred_arista = [-1] * n
    procesados = set()
    dist[origen] = 0
    pasos = []
    guardar(pasos, "Inicio: distancia del origen = 0.", None, None,
            procesados, (origen,), dist, pred, pred_arista)

    for vuelta in range(1, n):
        cambios = 0
        for arista in grafo.es:
            a, b = arista.tuple
            peso = int(arista["peso"])
            for u, v in ((a, b), (b, a)):
                if dist[u] == inf or dist[u] + peso >= dist[v]:
                    continue
                dist[v] = dist[u] + peso
                pred[v] = u
                pred_arista[v] = arista.index
                procesados.add(u)
                cambios += 1
                guardar(pasos,
                        f"Vuelta {vuelta}: {grafo.vs[u]['nombre']} → "
                        f"{grafo.vs[v]['nombre']}; nuevo costo {dist[v]} "
                        f"(arista de peso {peso}).",
                        u, arista.index, procesados, (v,), dist, pred, pred_arista)
        guardar(pasos, f"Fin de la vuelta {vuelta}: {cambios} mejoras.",
                None, None, procesados, (), dist, pred, pred_arista)
        if cambios == 0:
            break

    ruta, ruta_aristas, costo = reconstruir_ruta(
        grafo, origen, destino, pred, pred_arista)
    guardar(pasos,
            f"Terminado: costo mínimo {costo}." if ruta else "No hay ruta.",
            destino if ruta else None, None, procesados, (), dist, pred,
            pred_arista, True, ruta, ruta_aristas, costo)
    return pasos


def floyd_warshall_manual(grafo, _matriz, origen, destino):
    """Calcula todos los pares con programación dinámica, sin función de igraph.

    En cada paso se autoriza un nuevo vértice intermedio k. La tabla de la
    interfaz muestra la fila que corresponde al origen elegido por el usuario.
    """
    n = grafo.vcount()
    inf = float("inf")
    dist = [[inf] * n for _ in range(n)]
    siguiente = [[-1] * n for _ in range(n)]
    primera_arista = [[-1] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
        siguiente[i][i] = i
    for arista in grafo.es:
        a, b = arista.tuple
        peso = int(arista["peso"])
        for u, v in ((a, b), (b, a)):
            if peso < dist[u][v]:
                dist[u][v] = peso
                siguiente[u][v] = v
                primera_arista[u][v] = arista.index

    def estado_del_origen():
        """Obtiene predecesores de la fila del origen para la tabla visual."""
        pred = [-1] * n
        pred_arista = [-1] * n
        for objetivo in range(n):
            if objetivo == origen or siguiente[origen][objetivo] == -1:
                continue
            actual = origen
            vistos = set()
            while actual != objetivo and actual not in vistos:
                vistos.add(actual)
                previo = actual
                actual = siguiente[actual][objetivo]
                if actual == objetivo:
                    pred[objetivo] = previo
                    pred_arista[objetivo] = primera_arista[previo][objetivo]
            # Las entradas aún no completas permanecen con predecesor «—».
        return pred, pred_arista

    pasos = []
    pred, pred_arista = estado_del_origen()
    guardar(pasos, "Matriz inicial: costos directos y 0 en la diagonal.",
            None, None, set(), (), dist[origen], pred, pred_arista)

    for k in range(n):
        mejoras = 0
        for i in range(n):
            if dist[i][k] == inf:
                continue
            for j in range(n):
                if dist[k][j] == inf:
                    continue
                candidato = dist[i][k] + dist[k][j]
                if candidato < dist[i][j]:
                    dist[i][j] = candidato
                    siguiente[i][j] = siguiente[i][k]
                    primera_arista[i][j] = primera_arista[i][k]
                    mejoras += 1
        pred, pred_arista = estado_del_origen()
        guardar(pasos,
                f"Intermedio k = {grafo.vs[k]['nombre']}: "
                f"{mejoras} mejoras en la matriz de todos los pares.",
                k, None, set(range(k + 1)), (), dist[origen],
                pred, pred_arista)

    ruta = []
    ruta_aristas = []
    if siguiente[origen][destino] != -1:
        actual = origen
        ruta.append(actual)
        while actual != destino:
            eid = primera_arista[actual][destino]
            actual = siguiente[actual][destino]
            ruta_aristas.append(eid)
            ruta.append(actual)
            if len(ruta) > n:  # Defensa frente a datos inconsistentes.
                raise ValueError("Se detectó un ciclo al reconstruir Floyd-Warshall")
    costo = None if not ruta else dist[origen][destino]
    pred, pred_arista = estado_del_origen()
    guardar(pasos,
            f"Terminado: costo mínimo {costo}." if ruta else "No hay ruta.",
            destino if ruta else None, None, set(range(n)), (),
            dist[origen], pred, pred_arista, True,
            ruta, ruta_aristas, costo)
    return pasos


def bfs_manual(grafo, matriz, origen, destino):
    """Búsqueda en anchura: minimiza saltos, no necesariamente peso."""
    n = grafo.vcount()
    profundidad = [float("inf")] * n
    pred = [-1] * n
    pred_arista = [-1] * n
    descubiertos = {origen}
    visitados = set()
    cola = [origen]
    profundidad[origen] = 0
    pasos = []
    guardar(pasos, "Inicio de BFS: el origen entra en la cola.", None, None,
            visitados, cola, profundidad, pred, pred_arista)

    while cola:
        u = cola.pop(0)
        visitados.add(u)
        guardar(pasos, f"Se visita {grafo.vs[u]['nombre']} (nivel {profundidad[u]}).",
                u, None, visitados, cola, profundidad, pred, pred_arista)
        if u == destino:
            break
        for v in range(n):
            for eid, peso in matriz[u][v]:
                if v in descubiertos:
                    continue
                descubiertos.add(v)
                cola.append(v)
                profundidad[v] = profundidad[u] + 1
                pred[v] = u
                pred_arista[v] = eid
                guardar(pasos,
                        f"Se descubre {grafo.vs[v]['nombre']} desde "
                        f"{grafo.vs[u]['nombre']}; arista de peso {peso}, "
                        f"nivel {profundidad[v]}.",
                        u, eid, visitados, cola, profundidad, pred, pred_arista)

    ruta, ruta_aristas, costo = reconstruir_ruta(
        grafo, origen, destino, pred, pred_arista)
    mensaje = (f"Terminado: {len(ruta)-1} saltos, costo real {costo}."
               if ruta else "No hay ruta.")
    guardar(pasos, mensaje, destino if ruta else None, None, visitados, (),
            profundidad, pred, pred_arista, True, ruta, ruta_aristas, costo)
    return pasos


def dfs_manual(grafo, matriz, origen, destino):
    """Búsqueda en profundidad con retroceso manual, sin repetir nodos."""
    n = grafo.vcount()
    profundidad = [float("inf")] * n
    pred = [-1] * n
    pred_arista = [-1] * n
    visitados = set()
    pila = []
    pasos = []
    profundidad[origen] = 0
    guardar(pasos, "Inicio de DFS.", None, None, visitados, pila,
            profundidad, pred, pred_arista)

    def explorar(u):
        visitados.add(u)
        pila.append(u)
        guardar(pasos, f"Se entra en {grafo.vs[u]['nombre']}.", u, None,
                visitados, pila, profundidad, pred, pred_arista)
        if u == destino:
            return True
        for v in range(n):
            for eid, peso in matriz[u][v]:
                if v in visitados:
                    continue
                pred[v] = u
                pred_arista[v] = eid
                profundidad[v] = profundidad[u] + 1
                guardar(pasos,
                        f"Se sigue {grafo.vs[u]['nombre']} → "
                        f"{grafo.vs[v]['nombre']} (peso {peso}).",
                        u, eid, visitados, pila, profundidad, pred, pred_arista)
                if explorar(v):
                    return True
        pila.pop()
        guardar(pasos, f"Retroceso desde {grafo.vs[u]['nombre']}.", u, None,
                visitados, pila, profundidad, pred, pred_arista)
        return False

    explorar(origen)
    ruta, ruta_aristas, costo = reconstruir_ruta(
        grafo, origen, destino, pred, pred_arista)
    mensaje = (f"DFS encontró una ruta de costo {costo}; no garantiza mínimo."
               if ruta else "DFS terminó sin encontrar una ruta.")
    guardar(pasos, mensaje, destino if ruta else None, None, visitados, (),
            profundidad, pred, pred_arista, True, ruta, ruta_aristas, costo)
    return pasos


ALGORITMOS = {
    "Dijkstra (menor costo)": dijkstra_manual,
    "Bellman-Ford (menor costo)": bellman_ford_manual,
    "Floyd-Warshall (todos los pares)": floyd_warshall_manual,
    "BFS (menos saltos)": bfs_manual,
    "DFS (profundidad)": dfs_manual,
}


class Interfaz:
    def __init__(self, raiz):
        self.raiz = raiz
        self.grafo, self.indice, self.disposicion_original = construir_grafo()
        self.matriz = construir_matriz(self.grafo)
        self.disposicion = self.disposicion_original
        self.pasos = []
        self.paso_actual = 0
        self.reproduciendo = False
        self.origen = None
        self.destino = None
        self.var_a = tk.StringVar(value="6")
        self.var_b = tk.StringVar(value="44")
        self.var_algoritmo = tk.StringVar(value="Dijkstra (menor costo)")
        self.var_numero = tk.StringVar(value="0")
        self.var_velocidad = tk.IntVar(value=650)
        self._crear_ventana()
        self.preparar()

    def _crear_ventana(self):
        self.raiz.title("Explorador visual de grafos · igraph")
        self.raiz.geometry("1560x900")
        self.raiz.minsize(1150, 700)
        estilo = ttk.Style()
        if "clam" in estilo.theme_names():
            estilo.theme_use("clam")
        estilo.configure("TButton", padding=7)
        estilo.configure("TCombobox", padding=4)

        base = ttk.Frame(self.raiz, padding=12)
        base.pack(fill="both", expand=True)
        ttk.Label(base, text="Explorador visual del grafo ponderado",
                  font=("Arial", 19, "bold")).pack(anchor="w")
        ttk.Label(base,
                  text="30 nodos · 63 aristas · no dirigido · 12–16 tiene pesos 16 y 3",
                  font=("Arial", 10)).pack(anchor="w", pady=(2, 10))

        controles = ttk.Frame(base)
        controles.pack(fill="x", pady=(0, 8))
        nombres = [str(n) for n in self.grafo.vs["nombre"]]
        ttk.Label(controles, text="Nodo A · origen").pack(side="left", padx=(0, 5))
        ttk.Combobox(controles, textvariable=self.var_a, values=nombres,
                     width=6, state="readonly").pack(side="left", padx=(0, 16))
        ttk.Label(controles, text="Nodo B · destino").pack(side="left", padx=(0, 5))
        ttk.Combobox(controles, textvariable=self.var_b, values=nombres,
                     width=6, state="readonly").pack(side="left", padx=(0, 16))
        ttk.Label(controles, text="Algoritmo").pack(side="left", padx=(0, 5))
        ttk.Combobox(controles, textvariable=self.var_algoritmo,
                     values=list(ALGORITMOS), width=28,
                     state="readonly").pack(side="left", padx=(0, 10))
        ttk.Button(controles, text="Preparar búsqueda", command=self.preparar).pack(side="left")
        ttk.Button(controles, text="Cambiar disposición", command=self.cambiar_disposicion).pack(
            side="left", padx=8)

        cuerpo = ttk.Panedwindow(base, orient="horizontal")
        cuerpo.pack(fill="both", expand=True)
        izquierda = ttk.Frame(cuerpo)
        derecha = ttk.Frame(cuerpo, width=390, padding=(8, 0, 0, 0))
        cuerpo.add(izquierda, weight=4)
        cuerpo.add(derecha, weight=1)

        self.lienzo = tk.Canvas(izquierda, bg="#f7fbff", highlightthickness=1,
                                highlightbackground="#d7e3ee")
        self.lienzo.pack(fill="both", expand=True)
        self.lienzo.bind("<Configure>", lambda _e: self.dibujar())
        ttk.Label(izquierda,
                  text="Azul: pendiente   ·   Amarillo: frontera   ·   Verde: visitado   ·   Coral: actual   ·   Naranja: ruta final",
                  font=("Arial", 10)).pack(anchor="w", pady=6)

        ttk.Label(derecha, text="Animación", font=("Arial", 14, "bold")).pack(anchor="w")
        barra = ttk.Frame(derecha)
        barra.pack(fill="x", pady=7)
        ttk.Button(barra, text="⏮ Inicio", command=self.ir_inicio).pack(side="left")
        ttk.Button(barra, text="◀ Atrás", command=self.anterior).pack(side="left", padx=2)
        ttk.Button(barra, text="Siguiente ▶", command=self.siguiente).pack(side="left", padx=2)
        self.boton_auto = ttk.Button(barra, text="▶ Reproducir", command=self.alternar_auto)
        self.boton_auto.pack(side="left", padx=2)
        ttk.Label(derecha, text="Intervalo de animación (ms)").pack(anchor="w")
        tk.Scale(derecha, from_=150, to=1500, resolution=50,
                 orient="horizontal", variable=self.var_velocidad,
                 bg="#f0f5fa", highlightthickness=0).pack(fill="x")

        salto = ttk.Frame(derecha)
        salto.pack(fill="x", pady=5)
        self.etiqueta_paso = ttk.Label(salto, text="Paso 0 / 0")
        self.etiqueta_paso.pack(side="left", padx=(0, 12))
        ttk.Entry(salto, textvariable=self.var_numero, width=7).pack(side="left")
        ttk.Button(salto, text="Ir al paso", command=self.ir_a_paso).pack(side="left", padx=3)

        self.etiqueta_estado = ttk.Label(derecha, text="", wraplength=350,
                                         justify="left", font=("Arial", 11))
        self.etiqueta_estado.pack(fill="x", anchor="w", pady=(7, 10))
        self.etiqueta_resultado = ttk.Label(derecha, text="", wraplength=350,
                                            justify="left", font=("Arial", 11, "bold"))
        self.etiqueta_resultado.pack(fill="x", anchor="w", pady=(0, 10))

        ttk.Label(derecha, text="Estado de los nodos",
                  font=("Arial", 12, "bold")).pack(anchor="w")
        tabla_marco = ttk.Frame(derecha)
        tabla_marco.pack(fill="both", expand=True, pady=6)
        self.tabla = ttk.Treeview(tabla_marco,
                                  columns=("nodo", "valor", "pred", "estado"),
                                  show="headings", height=20)
        for col, titulo, ancho in (
            ("nodo", "Nodo", 52), ("valor", "Costo/nivel", 88),
            ("pred", "Previo", 67), ("estado", "Estado", 83)
        ):
            self.tabla.heading(col, text=titulo)
            self.tabla.column(col, width=ancho, anchor="center", stretch=True)
        desplazamiento = ttk.Scrollbar(tabla_marco, orient="vertical",
                                        command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=desplazamiento.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        desplazamiento.pack(side="right", fill="y")
        self.etiqueta_aclaracion = ttk.Label(derecha, text="", wraplength=350,
                                             justify="left")
        self.etiqueta_aclaracion.pack(fill="x", pady=5)

    def preparar(self):
        self.reproduciendo = False
        self.boton_auto.config(text="▶ Reproducir")
        try:
            a = int(self.var_a.get())
            b = int(self.var_b.get())
            self.origen = self.indice[a]
            self.destino = self.indice[b]
        except (ValueError, KeyError):
            messagebox.showerror("Nodos inválidos", "Elige dos nodos de la lista.")
            return
        algoritmo = self.var_algoritmo.get()
        self.pasos = ALGORITMOS[algoritmo](
            self.grafo, self.matriz, self.origen, self.destino)
        self.paso_actual = 0
        if algoritmo.startswith("BFS"):
            aclaracion = "BFS minimiza saltos; el costo mostrado suma los pesos de la ruta encontrada."
        elif algoritmo.startswith("DFS"):
            aclaracion = "DFS encuentra una ruta, pero no garantiza ni menor peso ni menos saltos."
        else:
            aclaracion = "Este algoritmo minimiza la suma de pesos de la ruta."
        self.etiqueta_aclaracion.config(text=aclaracion)
        self.actualizar()

    def ir_inicio(self):
        self.reproduciendo = False
        self.boton_auto.config(text="▶ Reproducir")
        self.paso_actual = 0
        self.actualizar()

    def anterior(self):
        self.reproduciendo = False
        self.boton_auto.config(text="▶ Reproducir")
        self.paso_actual = max(0, self.paso_actual - 1)
        self.actualizar()

    def siguiente(self):
        self.paso_actual = min(len(self.pasos) - 1, self.paso_actual + 1)
        self.actualizar()

    def ir_a_paso(self):
        try:
            numero = int(self.var_numero.get())
        except ValueError:
            messagebox.showerror("Paso inválido", "Escribe un número entero.")
            return
        if not 0 <= numero < len(self.pasos):
            messagebox.showerror("Paso inválido",
                                 f"Elige un paso de 0 a {len(self.pasos)-1}.")
            return
        self.reproduciendo = False
        self.boton_auto.config(text="▶ Reproducir")
        self.paso_actual = numero
        self.actualizar()

    def alternar_auto(self):
        self.reproduciendo = not self.reproduciendo
        self.boton_auto.config(text="⏸ Pausar" if self.reproduciendo else "▶ Reproducir")
        if self.reproduciendo:
            self._tick()

    def _tick(self):
        if not self.reproduciendo:
            return
        if self.paso_actual >= len(self.pasos) - 1:
            self.reproduciendo = False
            self.boton_auto.config(text="▶ Reproducir")
            return
        self.siguiente()
        self.raiz.after(self.var_velocidad.get(), self._tick)

    def cambiar_disposicion(self):
        if self.disposicion is self.disposicion_original:
            # igraph calcula solo la disposición visual; las búsquedas son manuales.
            self.disposicion = self.grafo.layout("fr")
        else:
            self.disposicion = self.disposicion_original
        self.dibujar()

    def actualizar(self):
        if not self.pasos:
            return
        paso = self.pasos[self.paso_actual]
        self.var_numero.set(str(self.paso_actual))
        self.etiqueta_paso.config(
            text=f"Paso {self.paso_actual} / {len(self.pasos)-1}")
        self.etiqueta_estado.config(text=paso.mensaje)
        if paso.terminado and paso.ruta:
            nombres = [str(self.grafo.vs[i]["nombre"]) for i in paso.ruta]
            self.etiqueta_resultado.config(
                text=f"Ruta: {' → '.join(nombres)}\n"
                     f"Costo total: {paso.costo} · Saltos: {len(nombres)-1}")
        elif paso.terminado:
            self.etiqueta_resultado.config(text="No existe una ruta.")
        else:
            self.etiqueta_resultado.config(text="")

        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for i, vertice in enumerate(self.grafo.vs):
            valor = paso.distancias[i]
            valor_texto = "∞" if valor == float("inf") else str(valor)
            previo = ("—" if paso.predecesores[i] == -1 else
                      str(self.grafo.vs[paso.predecesores[i]]["nombre"]))
            estado = ("Actual" if i == paso.actual else
                      "Visitado" if i in paso.visitados else
                      "Frontera" if i in paso.frontera else "Pendiente")
            self.tabla.insert("", "end", values=(vertice["nombre"],
                valor_texto, previo, estado))
        self.dibujar()

    def dibujar(self):
        if not hasattr(self, "lienzo") or not self.pasos:
            return
        ancho, alto = self.lienzo.winfo_width(), self.lienzo.winfo_height()
        if ancho < 100 or alto < 100:
            return
        self.lienzo.delete("all")
        paso = self.pasos[self.paso_actual]
        coords = [self.disposicion[i] for i in range(self.grafo.vcount())]
        min_x = min(x for x, _ in coords)
        max_x = max(x for x, _ in coords)
        min_y = min(y for _, y in coords)
        max_y = max(y for _, y in coords)
        escala = min((ancho - 80) / max(1, max_x-min_x),
                     (alto - 80) / max(1, max_y-min_y))

        def punto(i):
            x, y = coords[i]
            return (40 + (x-min_x)*escala + (ancho-80-(max_x-min_x)*escala)/2,
                    40 + (y-min_y)*escala + (alto-80-(max_y-min_y)*escala)/2)

        pares = {}
        for arista in self.grafo.es:
            clave = tuple(sorted(arista.tuple))
            pares.setdefault(clave, []).append(arista.index)
        ruta_aristas = set(paso.ruta_aristas) if paso.terminado else set()
        ruta_nodos = set(paso.ruta) if paso.terminado else set()

        # Las aristas se leen de igraph.es; cada paralela tiene su propio ID.
        for arista in self.grafo.es:
            a, b = arista.tuple
            eid = arista.index
            peso = int(arista["peso"])
            x1, y1 = punto(a)
            x2, y2 = punto(b)
            mx, my = (x1+x2)/2, (y1+y2)/2
            dx, dy = x2-x1, y2-y1
            longitud = math.hypot(dx, dy) or 1
            grupo = pares[tuple(sorted((a, b)))]
            desvio = 0 if len(grupo) == 1 else (-22 if eid == grupo[0] else 22)
            cx = mx - dy/longitud*desvio
            cy = my + dx/longitud*desvio
            activo = eid == paso.arista
            en_ruta = eid in ruta_aristas
            color = ("#ff6b45" if activo else "#ed8b24" if en_ruta else
                     "#825eb0" if len(grupo) > 1 else "#8ba2b6")
            grosor = 5 if activo or en_ruta else 2
            self.lienzo.create_line(x1, y1, cx, cy, x2, y2,
                                    fill=color, width=grosor, smooth=True)
            lx, ly = (x1+2*cx+x2)/4, (y1+2*cy+y2)/4
            texto = self.lienzo.create_text(
                lx, ly, text=str(peso), fill="#172e46",
                font=("Arial", 10, "bold"))
            caja = self.lienzo.bbox(texto)
            if caja:
                fondo = self.lienzo.create_rectangle(
                    caja[0]-3, caja[1]-2, caja[2]+3, caja[3]+2,
                    fill="#f7fbff", outline="")
                self.lienzo.tag_lower(fondo, texto)

        for vertice in self.grafo.vs:
            i = vertice.index
            x, y = punto(i)
            color = ("#ed8b24" if i in ruta_nodos else
                     "#ff6b45" if i == paso.actual else
                     "#56ae80" if i in paso.visitados else
                     "#e3b748" if i in paso.frontera else "#3989bc")
            radio = 20
            self.lienzo.create_oval(x-radio, y-radio, x+radio, y+radio,
                                    fill=color, outline="white", width=2)
            self.lienzo.create_text(x, y, text=str(vertice["nombre"]),
                                    fill="white", font=("Arial", 11, "bold"))


def main():
    raiz = tk.Tk()
    Interfaz(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()
