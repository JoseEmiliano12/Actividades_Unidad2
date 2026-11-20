"""Comprobaciones funcionales del grafo y las búsquedas manuales."""

import csv
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app
from rutas_simples import contar_sin_imprimir, generar_rutas


class ProyectoGrafos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grafo, cls.indice, _ = app.construir_grafo()
        cls.matriz = app.construir_matriz(cls.grafo)

    def test_datos_y_aristas_paralelas(self):
        self.assertEqual(self.grafo.vcount(), 30)
        self.assertEqual(self.grafo.ecount(), 63)
        pesos = sorted(p for _, p in self.matriz[self.indice[12]][self.indice[16]])
        self.assertEqual(pesos, [3, 16])
        self.assertEqual(
            self.matriz[self.indice[12]][self.indice[16]],
            self.matriz[self.indice[16]][self.indice[12]],
        )

    def test_csv_coincide_con_el_programa(self):
        archivo = Path(__file__).resolve().parents[1] / "aristas.csv"
        with archivo.open(encoding="utf-8", newline="") as f:
            filas = [tuple(int(fila[c]) for c in ("nodo_a", "nodo_b", "peso"))
                     for fila in csv.DictReader(f)]
        self.assertEqual(filas, app.ARISTAS)

    def test_costos_minimos_y_ruta(self):
        for a, b in ((6, 44), (44, 6), (12, 16), (6, 6), (21, 70)):
            origen, destino = self.indice[a], self.indice[b]
            resultados = [alg(self.grafo, self.matriz, origen, destino)[-1]
                          for alg in (app.dijkstra_manual,
                                      app.bellman_ford_manual,
                                      app.floyd_warshall_manual)]
            self.assertEqual(resultados[0].costo, resultados[1].costo)
            self.assertEqual(resultados[0].costo, resultados[2].costo)
            for paso in resultados:
                self.assertEqual(paso.ruta[0], origen)
                self.assertEqual(paso.ruta[-1], destino)
                self.assertEqual(
                    sum(self.grafo.es[eid]["peso"] for eid in paso.ruta_aristas),
                    paso.costo,
                )
        destino = self.indice[44]
        final = app.dijkstra_manual(self.grafo, self.matriz,
                                    self.indice[6], destino)[-1]
        self.assertEqual(final.costo, 81)
        self.assertEqual([self.grafo.vs[i]["nombre"] for i in final.ruta],
                         [6, 15, 0, 44])

    def test_bfs_dfs_y_backtracking_no_repiten_nodos(self):
        origen, destino = self.indice[6], self.indice[44]
        for algoritmo in (app.bfs_manual, app.dfs_manual):
            final = algoritmo(self.grafo, self.matriz, origen, destino)[-1]
            self.assertEqual(len(final.ruta), len(set(final.ruta)))
            self.assertEqual(final.ruta[0], origen)
            self.assertEqual(final.ruta[-1], destino)
        generador = generar_rutas(self.matriz, origen, destino)
        for _ in range(100):
            nodos, aristas, pesos, costo = next(generador)
            self.assertEqual(len(nodos), len(set(nodos)))
            self.assertEqual(sum(pesos), costo)
            self.assertEqual(len(aristas), len(nodos) - 1)

    def test_conteo_distingue_aristas_paralelas(self):
        # En este grafo pequeño hay dos rutas físicas 0→1 y una 0→2→1.
        matriz = [[[] for _ in range(3)] for _ in range(3)]
        matriz[0][1] = [(0, 3), (1, 16)]
        matriz[1][0] = matriz[0][1]
        matriz[0][2] = [(2, 2)]
        matriz[2][0] = matriz[0][2]
        matriz[2][1] = [(3, 1)]
        matriz[1][2] = matriz[2][1]
        total, minimas = contar_sin_imprimir(matriz, 0, 1, 3)
        self.assertEqual(total, 3)
        self.assertEqual(len(minimas), 2)


if __name__ == "__main__":
    unittest.main()
