"""
PROYECTO 1 - VISUALIZADOR INTERACTIVO
=====================================
Une en una sola ventana las tres versiones del AG binario del libro
"Algoritmos Evolutivos: un enfoque practico" (Araujo y Cervigon):

    v1  Maximizacion      f(x) = 20 + e - 20 e^(-0.2|x|) - e^(cos 2 pi x),  x en [0, 32]
    v2  Minimizacion      f(x) = -|x sen(sqrt(|x|))|,                       x en [-250, 250]
    v3  Varias variables  f(x) = sum( -x_i sen(sqrt(|x_i|)) ),              x_i en [0, 100]

Se usan TAL CUAL las funciones de v1_maximizar.py, v2_minimizar.py y
v3_varias_variables.py (seleccion, reproduccion, mutacion, evaluacion, ...).
Aqui solo se repite el bucle del main() de cada version para guardar
cada generacion y poder recorrerlas en la ventana.

Ejecutar:
    python app_proyecto1.py
"""

import math
import os
import random
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.dirname(AQUI))  # para importar visor_ag.py

from PySide6.QtWidgets import QComboBox, QDoubleSpinBox, QSpinBox  # noqa: E402

import v1_maximizar  # noqa: E402
import v2_minimizar  # noqa: E402
import v3_varias_variables  # noqa: E402
from visor_ag import Resultado, VentanaAG, iniciar  # noqa: E402

VERSIONES = {
    "v1": dict(nombre="v1 · Maximización", modulo=v1_maximizar, x_min=0.0, x_max=32.0,
               formula="f(x) = 20 + e − 20·e^(−0.2|x|) − e^(cos 2πx)",
               optimo=lambda n: 22.3136, x_opt=lambda n: [31.5005],
               nota="Máximo según el libro: 22.3136 en x = 31.5005"),
    "v2": dict(nombre="v2 · Minimización", modulo=v2_minimizar, x_min=-250.0, x_max=250.0,
               formula="f(x) = −|x·sen(√|x|)|",
               optimo=lambda n: -201.843, x_opt=lambda n: [203.814],
               nota="Mínimo según el libro: −201.843 en x = ±203.814.\n"
                    "La aptitud se transforma con revisar_adap_mini (cmax − f)."),
    "v3": dict(nombre="v3 · Varias variables", modulo=v3_varias_variables, x_min=0.0, x_max=100.0,
               formula="f(x) = Σ −xᵢ·sen(√|xᵢ|)",
               optimo=lambda n: -n * 63.63498, x_opt=lambda n: [65.54785] * n,
               nota="Mínimo según el libro: −n·63.63498 en xᵢ = 65.54785 (para xᵢ en [0, 100]).\n"
                    "Cada variable tiene su propio cromosoma y su punto de cruce."),
}


def correr_version(v, x_min, x_max, TOL, tam_pob, num_gen, prob_cruce, prob_mut, num_var,
                   semilla, progreso):
    """Mismo bucle que el main() de cada version, guardando cada generacion."""
    mod = VERSIONES[v]["modulo"]
    random.seed(time.time() if semilla is None else semilla)

    if v == "v3":
        mod.NUM_VAR = num_var
        x_min = [x_min] * num_var
        x_max = [x_max] * num_var
        lcrom = [int(math.ceil(math.log(1 + (x_max[i] - x_min[i]) / TOL) / math.log(2.0)))
                 for i in range(num_var)]
    else:
        lcrom = int(math.ceil(math.log(1 + (x_max - x_min) / TOL) / math.log(2.0)))

    poblaciones, valores = [], []

    def registrar():
        if v == "v1":
            poblaciones.append([[ind.x] for ind in pob])
            valores.append([ind.aptitud for ind in pob])
        elif v == "v2":
            poblaciones.append([[ind.x] for ind in pob])
            valores.append([ind.aptitud_bruta for ind in pob])
        else:
            poblaciones.append([list(ind.vec_x) for ind in pob])
            valores.append([ind.aptitud_bruta for ind in pob])

    # se genera la poblacion inicial y se evalua
    pob = mod.poblacion_inicial(tam_pob, lcrom, x_min, x_max)
    cmax = 0.0
    if v != "v1":
        cmax = mod.revisar_adap_mini(pob, tam_pob, lcrom, cmax, x_min, x_max)
    pos_mejor = 0
    pos_mejor, _ = mod.evaluacion(pob, tam_pob, pos_mejor)
    registrar()

    # bucle de evolucion
    for generacion in range(num_gen):
        mod.seleccion(pob, tam_pob)
        mod.reproduccion(pob, tam_pob, lcrom, prob_cruce, x_min, x_max)
        mod.mutacion(pob, tam_pob, lcrom, prob_mut, x_min, x_max)
        if v != "v1":
            cmax = mod.revisar_adap_mini(pob, tam_pob, lcrom, cmax, x_min, x_max)
        pos_mejor, _ = mod.evaluacion(pob, tam_pob, pos_mejor)
        registrar()
        progreso((generacion + 1) / num_gen)

    if v == "v3":
        funcion = lambda x: mod.funcion(list(x))  # noqa: E731
        xmin_l, xmax_l = x_min, x_max
    else:
        funcion = lambda x: mod.funcion(float(x[0]))  # noqa: E731
        xmin_l, xmax_l = [x_min], [x_max]
    datos = VERSIONES[v]
    n = num_var if v == "v3" else 1
    titulo = f"Proyecto 1 · {datos['nombre']}  —  {datos['formula']}"
    if v == "v3":
        titulo += f"   (n = {n})"
    return Resultado(titulo=titulo, funcion=funcion, x_min=xmin_l, x_max=xmax_l,
                     maximizar=(v == "v1"), poblaciones=poblaciones, valores=valores,
                     optimo=datos["optimo"](n), x_opt=datos["x_opt"](n))


def spin(minimo, maximo, valor, paso=1.0, decimales=None):
    if decimales is None:
        w = QSpinBox()
    else:
        w = QDoubleSpinBox()
        w.setDecimals(decimales)
    w.setRange(minimo, maximo)
    w.setSingleStep(paso)
    w.setValue(valor)
    return w


class VentanaProyecto1(VentanaAG):
    def __init__(self):
        super().__init__("Proyecto 1 · AG binario",
                         "Algoritmos Evolutivos (Araujo y Cervigon) · Apéndice B: "
                         "maximización, minimización y varias variables")

    def construir_parametros(self):
        self.version = QComboBox()
        for clave, d in VERSIONES.items():
            self.version.addItem(d["nombre"], clave)
        self.x_min = spin(-100000, 100000, 0.0, 1.0, 4)
        self.x_max = spin(-100000, 100000, 32.0, 1.0, 4)
        self.tol = spin(0.000001, 1.0, 0.0001, 0.0001, 6)
        self.tol.setToolTip("Precisión con la que se busca el óptimo: define la longitud del cromosoma")
        self.tam_pob = spin(4, 5000, 100, 10)
        self.num_gen = spin(1, 5000, 100, 10)
        self.prob_cruce = spin(0.0, 1.0, 0.6, 0.05, 3)
        self.prob_mut = spin(0.0, 1.0, 0.05, 0.005, 3)
        self.num_var = spin(1, 30, 2)
        self.num_var.setToolTip("NUM_VAR: número de variables (solo v3)")
        self.semilla = spin(-1, 999999, -1)
        self.semilla.setSpecialValueText("aleatoria")
        self.semilla.setToolTip("Fija una semilla para repetir exactamente la misma ejecución")

        for etiqueta, w in [("Versión", self.version), ("x mínimo", self.x_min), ("x máximo", self.x_max),
                            ("Precisión (TOL)", self.tol), ("Tamaño población", self.tam_pob),
                            ("Generaciones", self.num_gen), ("Prob. de cruce", self.prob_cruce),
                            ("Prob. de mutación", self.prob_mut), ("Nº de variables", self.num_var),
                            ("Semilla", self.semilla)]:
            self.form.addRow(etiqueta, w)

        self.version.currentIndexChanged.connect(self._cambiar_version)
        self.num_var.valueChanged.connect(lambda _: self._actualizar_info())
        self.x_min.valueChanged.connect(lambda _: self._actualizar_info())
        self.x_max.valueChanged.connect(lambda _: self._actualizar_info())
        self.tol.valueChanged.connect(lambda _: self._actualizar_info())
        self._cambiar_version()

    def _cambiar_version(self):
        v = self.version.currentData()
        d = VERSIONES[v]
        self.x_min.setValue(d["x_min"])
        self.x_max.setValue(d["x_max"])
        self.num_var.setEnabled(v == "v3")
        self._actualizar_info()

    def _actualizar_info(self):
        v = self.version.currentData()
        d = VERSIONES[v]
        rango = self.x_max.value() - self.x_min.value()
        bits = "—"
        if rango > 0 and self.tol.value() > 0:
            bits = int(math.ceil(math.log(1 + rango / self.tol.value()) / math.log(2.0)))
            if v == "v3":
                bits = f"{bits} por variable × {self.num_var.value()} = {bits * self.num_var.value()}"
        self.info(f"<b>{d['formula']}</b><br>{d['nota'].replace(chr(10), '<br>')}"
                  f"<br><br>Longitud del cromosoma: <b>{bits}</b> bits")

    def leer_parametros(self):
        if self.x_min.value() >= self.x_max.value():
            raise ValueError("x mínimo debe ser menor que x máximo.")
        if self.tol.value() <= 0:
            raise ValueError("La precisión (TOL) debe ser mayor que 0.")
        s =self.semilla.value()
        return dict(v=self.version.currentData(), x_min=self.x_min.value(), x_max=self.x_max.value(),
                    TOL=self.tol.value(), tam_pob=self.tam_pob.value(), num_gen=self.num_gen.value(),
                    prob_cruce=self.prob_cruce.value(), prob_mut=self.prob_mut.value(),
                    num_var=self.num_var.value(), semilla=None if s < 0 else s)

    def ejecutar(self, p, progreso):
        return correr_version(p["v"], p["x_min"], p["x_max"], p["TOL"], p["tam_pob"], p["num_gen"],
                              p["prob_cruce"], p["prob_mut"], p["num_var"], p["semilla"], progreso)


if __name__ == "__main__":
    iniciar(VentanaProyecto1)
