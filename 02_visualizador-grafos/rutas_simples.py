"""Enumera rutas simples entre dos nodos usando backtracking manual.

Ejemplos:
    python rutas_simples.py 6 44 --solo-resumen
    python rutas_simples.py 44 6 --salida todas_las_rutas.txt
"""

import argparse
from contextlib import nullcontext

from app import construir_grafo, construir_matriz, dijkstra_manual


def generar_rutas(matriz, origen, destino):
    """Genera una ruta cada vez; distingue las dos aristas 12–16."""
    n = len(matriz)
    visitado = [False] * n
    camino = [origen]
    aristas = []
    pesos = []
    visitado[origen] = True

    def explorar(u, costo):
        if u == destino:
            yield camino.copy(), aristas.copy(), pesos.copy(), costo
            return
        for v in range(n):
            if visitado[v]:
                continue
            for eid, peso in matriz[u][v]:
                visitado[v] = True
                camino.append(v)
                aristas.append(eid)
                pesos.append(peso)
                yield from explorar(v, costo + peso)
                pesos.pop()
                aristas.pop()
                camino.pop()
                visitado[v] = False

    yield from explorar(origen, 0)


def contar_sin_imprimir(matriz, origen, destino, costo_minimo):
    """Cuenta sin construir una copia de cada ruta; útil para millones de rutas."""
    n = len(matriz)
    visitado = [False] * n
    camino = [origen]
    visitado[origen] = True
    total = 0
    minimas = []

    def explorar(u, costo):
        nonlocal total
        if u == destino:
            total += 1
            if costo == costo_minimo:
                minimas.append((total, camino.copy()))
            return
        for v in range(n):
            if visitado[v]:
                continue
            for _eid, peso in matriz[u][v]:
                visitado[v] = True
                camino.append(v)
                explorar(v, costo + peso)
                camino.pop()
                visitado[v] = False

    explorar(origen, 0)
    return total, minimas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("origen", type=int, nargs="?", default=6)
    parser.add_argument("destino", type=int, nargs="?", default=44)
    parser.add_argument("--solo-resumen", action="store_true",
                        help="Cuenta sin imprimir las rutas individuales")
    parser.add_argument("--salida", metavar="ARCHIVO",
                        help="Guarda la enumeración completa en un archivo de texto")
    args = parser.parse_args()
    grafo, indice, _ = construir_grafo()
    if args.origen not in indice or args.destino not in indice:
        parser.error("origen y destino deben ser nodos presentes en el grafo")
    origen, destino = indice[args.origen], indice[args.destino]
    matriz = construir_matriz(grafo)
    mejor = dijkstra_manual(grafo, matriz, origen, destino)[-1]

    if args.solo_resumen:
        total, minimas = contar_sin_imprimir(
            matriz, origen, destino, mejor.costo)
        print(f"TOTAL DE RUTAS SIN REPETIR NODOS: {total}")
        print(f"Costo mínimo según Dijkstra: {mejor.costo}")
        print(f"Cantidad de rutas de costo mínimo: {len(minimas)}")
        for numero, nodos in minimas:
            nombres = [grafo.vs[i]["nombre"] for i in nodos]
            print(f"Ruta {numero}: {' -> '.join(map(str, nombres))} "
                  f"| Costo: {mejor.costo}")
        return

    total = 0
    minimas = 0
    minimas_detalle = []
    archivo = open(args.salida, "w", encoding="utf-8") if args.salida else nullcontext()
    with archivo as salida:
        for nodos, aristas, pesos, costo in generar_rutas(matriz, origen, destino):
            total += 1
            nombres = [grafo.vs[i]["nombre"] for i in nodos]
            if costo == mejor.costo:
                minimas += 1
                minimas_detalle.append((total, nombres, pesos))
            if args.solo_resumen:
                continue
            texto = (f"Ruta {total}:\n"
                     f"{' -> '.join(map(str, nombres))}\n"
                     f"Costo: {costo}\n")
            if 12 in nombres and 16 in nombres:
                for a, b, peso in zip(nombres, nombres[1:], pesos):
                    if {a, b} == {12, 16}:
                        texto += f"Arista 12–16 utilizada: peso {peso}\n"
            if costo == mejor.costo:
                texto += "RUTA DE COSTO MÍNIMO\n"
            print(texto, file=salida)

    print(f"TOTAL DE RUTAS SIN REPETIR NODOS: {total}")
    print(f"Costo mínimo según Dijkstra: {mejor.costo}")
    print(f"Cantidad de rutas de costo mínimo: {minimas}")
    for numero, nodos, pesos in minimas_detalle:
        print(f"Ruta {numero}: {' -> '.join(map(str, nodos))} | Costo: {mejor.costo}")
    if args.salida and not args.solo_resumen:
        print(f"Enumeración completa guardada en: {args.salida}")


if __name__ == "__main__":
    main()
