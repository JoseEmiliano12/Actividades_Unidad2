"""
/******************************************************************/
/* Programacion evolutiva: proyecto 1                             */
/* version 3.0: VARIAS VARIABLES                                  */
/* Modulo funciones.cpp  (traducido de C++ a Python)              */
/******************************************************************/

Traduccion del codigo C++ "Funciones.h / Funciones.cpp para varias variables"
del Apendice B del libro "Algoritmos Evolutivos: un enfoque practico"
(Araujo y Cervigon), pags. 313-316.

El libro solo muestra las funciones que cambian respecto a la version de
minimizar (genera_indiv, adaptacion, cruce y mutacion). Las demas
(seleccion, evaluacion, revisar_adap_mini, poblacion_inicial, decod, bin_dec)
son las mismas de la version 2; reproduccion y main se adaptaron lo minimo
para manejar un vector de longitudes y de puntos de cruce (uno por variable).
Lo unico agregado es el HISTORIAL por generacion y las GRAFICAS (al final del archivo).
No se usa DEAP.

Representa la funcion:
    f(x_i | i = 1..n) = sum( -x_i sen(sqrt(|x_i|)) ),   x_i en [0, 100]
que tiene un valor de -n * 63.63498 y se encuentra en x_i = 65.54785.

El numero de variables es la constante NUM_VAR (como en el C++).

Uso (mismos parametros que el programa C++; x_min y x_max valen para todas las variables):
    python v3_varias_variables.py x_min x_max TOL tam_pob num_gen prob_cruce prob_mut [--gif archivo.gif]
Ejemplo:
    python v3_varias_variables.py 0 100 0.0001 100 100 0.6 0.05
"""

import math
import random
import sys
import time

import numpy as np

NUM_VAR = 2  # numero de variables de la funcion

# rand() y RAND_MAX como en C
RAND_MAX = 2147483647


def rand():
    return random.randint(0, RAND_MAX)


# ---------------------------------------------------------------------------
# Funciones.h para varias variables
# Necesitamos representar ahora los genes correspondientes a cada una de las
# variables involucradas. Extendemos por lo tanto la representacion del individuo:
#   typedef vector<bool>   TGenes;      // cadena de bits (genotipo)
#   typedef vector<TGenes> Tvec_genes;  // vector de genotipos de cada variable
#   typedef vector<float>  Tvec_var;    // vector de fenotipos de cada variable
#   typedef vector<int>    Tvec_int;    // vector para la longitudes de los genes
# ---------------------------------------------------------------------------
class TIndividuo:
    def __init__(self):
        self.vec_genes = []        # vector de genotipos (una cadena de bits por variable)
        self.vec_x = []            # fenotipo
        self.aptitud_bruta = 0.0   # funcion de evaluacion
        self.aptitud = 0.0         # aptitud transformada
        self.puntuacion = 0.0      # punt. relativa: fitness/sumfitness
        self.punt_acu = 0.0        # puntuacion acumulada para sorteos
        self.elite = False         # indicativo de pertenecer a la elite


def copia(ind):
    """En C++ los struct se copian por valor; en Python hay que copiarlos a mano."""
    nuevo = TIndividuo()
    nuevo.vec_genes = [list(g) for g in ind.vec_genes]
    nuevo.vec_x = list(ind.vec_x)
    nuevo.aptitud_bruta = ind.aptitud_bruta
    nuevo.aptitud = ind.aptitud
    nuevo.puntuacion = ind.puntuacion
    nuevo.punt_acu = ind.punt_acu
    nuevo.elite = ind.elite
    return nuevo


# ---------------------------------------------------------------------------
# funcion: revisar_adap_mini  (igual que en la version 2)
# Revisa la aptitud de la pob para transforma mini en maxi
# ---------------------------------------------------------------------------
def revisar_adap_mini(pob, tam_pob, lcrom, cmax, x_min, x_max):
    cmax = pob[0].aptitud_bruta
    for i in range(1, tam_pob):
        if pob[i].aptitud > cmax:
            cmax = pob[i].aptitud_bruta
    cmax = cmax + cmax / 100
    for i in range(tam_pob):
        pob[i].aptitud = cmax - pob[i].aptitud_bruta
    return cmax


# ---------------------------------------------------------------------------
# funcion: poblacion_inicial  (igual que en la version 2)
# ---------------------------------------------------------------------------
def poblacion_inicial(tam_pob, lcrom, x_min, x_max):
    pob = []
    for i in range(tam_pob):
        indiv = genera_indiv(lcrom, x_min, x_max)
        pob.append(indiv)
    return pob


# ---------------------------------------------------------------------------
# funcion: genera_indiv
# Genera un individuo de la poblacion inicial
# ---------------------------------------------------------------------------
def genera_indiv(lcrom, x_min, x_max):
    indiv = TIndividuo()
    indiv.vec_genes.clear()
    # ---------------------------------------------- #
    # se generan los genotipos para cada variable    #
    # ---------------------------------------------- #
    for i in range(NUM_VAR):
        genes = []
        for j in range(lcrom[i]):
            f = rand()
            if f < RAND_MAX / 2:
                gen = 0
            else:
                gen = 1
            genes.append(gen)
        indiv.vec_genes.append(genes)
    indiv.aptitud_bruta = adaptacion(indiv, lcrom, x_min, x_max)
    return indiv


# ---------------------------------------------------------------------------
# funcion: seleccion  (igual que en la version 2)
# Selecciona un unico individuo por el metodo de la ruleta
# ---------------------------------------------------------------------------
def seleccion(pob, tam_pob):
    TAM_ELITE = len(pob) * 2 // 100

    sel_super = [0] * tam_pob        # seleccionados para sobrevivir
    sel_elite = [0] * TAM_ELITE
    # se selecciona la elite
    for i in range(TAM_ELITE):
        sel_elite[i] = 0
    for i in range(tam_pob):
        pob[i].elite = False
        j = 0
        while (j < TAM_ELITE) and (pob[sel_elite[j]].aptitud >= pob[i].aptitud):
            j += 1
        if j < TAM_ELITE:
            sel_elite[j] = i
    for i in range(TAM_ELITE):
        pob[sel_elite[i]].elite = True

    # se seleccionan tam_pob individuos para reproducirse
    for i in range(tam_pob):
        if pob[i].elite:  # ELITISMO
            sel_super[i] = i
        else:
            f = rand()
            prob = f / (RAND_MAX + 1.0)
            pos_super = 0
            # (en C++ se revisa primero punt_acu; aqui se revisa primero el limite
            #  para no salirse de la lista)
            while (pos_super < tam_pob) and (prob > pob[pos_super].punt_acu):
                pos_super += 1
            if pos_super < tam_pob:
                sel_super[i] = pos_super
            else:
                sel_super[i] = pos_super - 1

    # se genera la poblacion intermedia
    pob_aux = []
    for i in range(tam_pob):
        pob_aux.append(copia(pob[sel_super[i]]))
    pob.clear()
    for i in range(tam_pob):
        pob.append(pob_aux[i])


# ---------------------------------------------------------------------------
# funcion: adaptacion
# Evalua la calidad de un individuo
# ---------------------------------------------------------------------------
def funcion(x):
    # AQUI se especifica la funcion a optimizar
    f = 0
    for i in range(NUM_VAR):
        f = f - x[i] * math.sin(math.sqrt(math.fabs(x[i])))
    return f


def adaptacion(individuo, lcrom, x_min, x_max):
    individuo.vec_x.clear()
    for i in range(NUM_VAR):
        individuo.vec_x.append(decod(individuo.vec_genes[i], lcrom[i], x_min[i], x_max[i]))
    x = individuo.vec_x  # vector de fenotipos
    f = funcion(x)       # valor de la funcion a optimizar
    return f


# ---------------------------------------------------------------------------
# funcion: decod / bin_dec  (iguales que en la version 2)
# ---------------------------------------------------------------------------
def decod(genes, lcrom, x_min, x_max):
    x = bin_dec(genes, lcrom) / (math.pow(2.0, lcrom) - 1)
    x = x_min + (x_max - x_min) * x
    return x


def bin_dec(genes, lcrom):
    d, pot = 0, 1
    for i in range(lcrom):
        d = d + pot * genes[i]
        pot = pot * 2
    return d


# ---------------------------------------------------------------------------
# funcion: reproduccion
# Igual que en la version 2, pero ahora lcrom y punto_cruce son vectores
# (un punto de cruce para cada variable)
# ---------------------------------------------------------------------------
def reproduccion(pob, tam_pob, lcrom, prob_cruce, x_min, x_max):
    sel_cruce = [0] * tam_pob  # seleccionados para reproducirse
    num_sel_cruce = 0          # num de individuos seleccionados para cruzar

    # se eligen los individuos a cruzar
    for i in range(tam_pob):
        prob = rand() / (RAND_MAX + 1.0)
        if prob < prob_cruce:
            sel_cruce[num_sel_cruce] = i
            num_sel_cruce += 1

    # el numero de seleccionados se hace par
    if (num_sel_cruce % 2) == 1:
        num_sel_cruce -= 1

    # se cruzan los individuos elegidos en un punto al azar (uno por variable)
    punto_cruce = []
    for j in range(NUM_VAR):
        punto_cruce.append(int(rand() * (lcrom[j] + 1) / (RAND_MAX + 1.0)) + 1)
    for i in range(0, num_sel_cruce, 2):
        hijo1, hijo2 = cruce(pob[sel_cruce[i]], pob[sel_cruce[i + 1]],
                             lcrom, punto_cruce, x_min, x_max)
        # los nuevos individuos sustituyen a sus progenitores
        # respetando la elite
        if (hijo1.aptitud < adaptacion(pob[sel_cruce[i]], lcrom, x_min, x_max)) or \
                (not pob[sel_cruce[i]].elite):  # ELITISMO
            pob[sel_cruce[i]] = hijo1
        if (hijo2.aptitud < adaptacion(pob[sel_cruce[i + 1]], lcrom, x_min, x_max)) or \
                (not pob[sel_cruce[i + 1]].elite):
            pob[sel_cruce[i + 1]] = hijo2


# ---------------------------------------------------------------------------
# funcion: cruce
# Aplica el operador de cruce
# ---------------------------------------------------------------------------
def cruce(padre1, padre2, lcrom, punto_cruce, x_min, x_max):
    hijo1, hijo2 = TIndividuo(), TIndividuo()
    hijo1.vec_genes.clear()
    hijo2.vec_genes.clear()

    for j in range(NUM_VAR):
        # primera parte del intercambio: 1 a 1 y 2 a 2
        genes_hijo1 = []
        genes_hijo2 = []
        # (punto_cruce puede valer lcrom+1; en C++ se leeria fuera del vector,
        #  aqui se limita a lcrom para que no falle)
        for i in range(min(punto_cruce[j], lcrom[j])):
            genes_hijo1.append(padre1.vec_genes[j][i])
            genes_hijo2.append(padre2.vec_genes[j][i])
        # segunda parte: 1 a 2 y 2 a 1
        for i in range(punto_cruce[j], lcrom[j]):
            genes_hijo1.append(padre2.vec_genes[j][i])
            genes_hijo2.append(padre1.vec_genes[j][i])
        hijo1.vec_genes.append(genes_hijo1)
        hijo2.vec_genes.append(genes_hijo2)
    # se evaluan
    hijo1.aptitud_bruta = adaptacion(hijo1, lcrom, x_min, x_max)
    hijo2.aptitud_bruta = adaptacion(hijo2, lcrom, x_min, x_max)
    return hijo1, hijo2


# ---------------------------------------------------------------------------
# funcion: mutacion
# Aplica el operador de mutacion a la poblacion
# ---------------------------------------------------------------------------
def mutacion(pob, tam_pob, lcrom, prob_mut, x_min, x_max):
    for i in range(tam_pob):
        mutado = False
        for k in range(NUM_VAR):
            for j in range(lcrom[k]):
                # se genera un numero aleatorio en [0 1)
                f = rand()
                prob = f / (RAND_MAX + 1.0)
                # se mutan aquellos genes con prob < que prob_mut
                if (prob < prob_mut) and (not pob[i].elite):
                    pob[i].vec_genes[k][j] = int(not bool(pob[i].vec_genes[k][j]))
                    mutado = True
        if mutado:
            pob[i].aptitud_bruta = adaptacion(pob[i], lcrom, x_min, x_max)


# ---------------------------------------------------------------------------
# funcion: evaluacion  (igual que en la version 2)
# ---------------------------------------------------------------------------
def evaluacion(pob, tam_pob, pos_mejor):
    punt_acu = 0          # puntuacion acumulada de los individuos
    aptitud_mejor = 0     # mejor aptitud
    sumaptitud = 0        # suma de la aptitud

    for i in range(tam_pob):
        sumaptitud = sumaptitud + pob[i].aptitud
        if pob[i].aptitud > aptitud_mejor:
            pos_mejor = i
            aptitud_mejor = pob[i].aptitud
    for i in range(tam_pob):
        pob[i].puntuacion = pob[i].aptitud / sumaptitud
        pob[i].punt_acu = pob[i].puntuacion + punt_acu
        punt_acu = punt_acu + pob[i].puntuacion
    return pos_mejor, sumaptitud


# =============================================================================
# =============================================================================
#   GRAFICAS E HISTORIAL
#   (Esto NO esta en el codigo C++ del libro: se agrego para poder graficar
#    la funcion y ver como se mueven los individuos en cada generacion)
# =============================================================================
# =============================================================================
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.widgets import Button, Slider

AZUL, NARANJA, GRIS, AMARILLO = "#2a78d6", "#eb6834", "#8a8984", "#eda100"


class Historial:
    """Guarda lo que pasa en cada generacion."""

    def __init__(self, maximizar):
        self.maximizar = maximizar
        self.poblaciones = []     # fenotipo (x) de cada individuo, por generacion
        self.valores = []         # valor de la funcion de cada individuo, por generacion
        self.pos_mejor = []       # posicion del mejor individuo, por generacion
        self.mejor = []           # valor del mejor de cada generacion
        self.media = []           # valor medio de cada generacion
        self.mejor_absoluto = []  # mejor valor encontrado hasta cada generacion

    def registrar(self, xs, fs, pos_mejor):
        xs = np.array(xs, dtype=float).reshape(len(xs), -1)
        fs = np.array(fs, dtype=float)
        self.poblaciones.append(xs)
        self.valores.append(fs)
        self.pos_mejor.append(pos_mejor)
        self.mejor.append(fs[pos_mejor])
        self.media.append(fs.mean())
        if not self.mejor_absoluto:
            self.mejor_absoluto.append(fs[pos_mejor])
        elif self.maximizar:
            self.mejor_absoluto.append(max(self.mejor_absoluto[-1], fs[pos_mejor]))
        else:
            self.mejor_absoluto.append(min(self.mejor_absoluto[-1], fs[pos_mejor]))


class Visualizador:
    """Ventana con la funcion, los individuos de la generacion elegida,
    la evolucion del mejor y la media, y controles para recorrer las generaciones."""

    def __init__(self, hist, funcion, x_min, x_max, titulo, interactivo=True):
        self.h, self.funcion = hist, funcion
        self.x_min, self.x_max = list(x_min), list(x_max)
        self.n = len(self.x_min)
        self.num_gen = len(hist.poblaciones) - 1
        self.gen = 0
        self.reproduciendo = False

        self.fig = plt.figure(figsize=(10, 8.5 if interactivo else 7.8))
        ancho = 0.70 if self.n != 2 else 0.86
        if interactivo:
            self.ax = self.fig.add_axes([0.08, 0.50, ancho, 0.38])
            self.ax_ev = self.fig.add_axes([0.08, 0.17, 0.70, 0.24])
        else:
            self.ax = self.fig.add_axes([0.08, 0.43, ancho, 0.45])
            self.ax_ev = self.fig.add_axes([0.08, 0.07, 0.70, 0.26])
        self.fig.suptitle(titulo, fontsize=12, fontweight="bold")

        self.dibujar_funcion()
        self.dibujar_evolucion()
        if interactivo:
            self.crear_controles()
        self.actualizar(0)

    def dibujar_funcion(self):
        ax = self.ax
        if self.n == 1:
            xs = np.linspace(self.x_min[0], self.x_max[0], 3000)
            ax.plot(xs, [self.funcion(np.array([x])) for x in xs], color=AZUL, lw=1.2, zorder=1)
            ax.set_xlabel("x")
            ax.set_ylabel("f(x)")
            self.puntos = ax.scatter([], [], s=28, color=NARANJA, edgecolor="white", lw=0.6,
                                     zorder=3, label="Individuos")
            self.estrella, = ax.plot([], [], "*", ms=16, color="black", zorder=4,
                                     label="Mejor de la generación")
            ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), fontsize=8)
        elif self.n == 2:
            g1 = np.linspace(self.x_min[0], self.x_max[0], 200)
            g2 = np.linspace(self.x_min[1], self.x_max[1], 200)
            X, Y = np.meshgrid(g1, g2)
            Z = np.array([[self.funcion(np.array([a, b])) for a, b in zip(fa, fb)]
                          for fa, fb in zip(X, Y)])
            cs = ax.contourf(X, Y, Z, levels=30,
                             cmap="Blues" if self.h.maximizar else "Blues_r", zorder=1)
            self.fig.colorbar(cs, ax=ax, fraction=0.04, pad=0.01, label="f(x1, x2)")
            ax.set_xlabel("x1")
            ax.set_ylabel("x2")
            ax.set_xlim(self.x_min[0], self.x_max[0])
            ax.set_ylim(self.x_min[1], self.x_max[1])
            self.puntos = ax.scatter([], [], s=26, color=NARANJA, edgecolor="white", lw=0.6,
                                     zorder=3, label="Individuos")
            self.estrella, = ax.plot([], [], "*", ms=17, color=AMARILLO, markeredgecolor="black",
                                     zorder=4, label="Mejor de la generación")
            ax.legend(loc="upper right", fontsize=8, framealpha=0.9)
        else:
            # 3 o mas variables: cada columna es una variable y cada punto un individuo
            ax.set_xlim(0.4, self.n + 0.6)
            ax.set_ylim(min(self.x_min), max(self.x_max))
            ax.set_xticks(range(1, self.n + 1))
            ax.set_xticklabels([f"x{i}" for i in range(1, self.n + 1)])
            ax.set_ylabel("Valor de la variable")
            self.puntos = ax.scatter([], [], s=14, color=NARANJA, alpha=0.6, zorder=3,
                                     label="Individuos")
            self.estrella, = ax.plot([], [], "*-", ms=12, color=AZUL, lw=1, zorder=4,
                                     label="Mejor de la generación")
            ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), fontsize=8)
        ax.grid(alpha=0.25)

    def dibujar_evolucion(self):
        ax, h = self.ax_ev, self.h
        gens = np.arange(len(h.mejor))
        ax.plot(gens, h.media, color=GRIS, lw=1.2, label="Media de la población")
        ax.plot(gens, h.mejor_absoluto, color=AZUL, lw=2.5, label="Mejor absoluto")
        ax.plot(gens, h.mejor, color=NARANJA, lw=1, ls="--", label="Mejor de la generación")
        self.linea_gen = ax.axvline(0, color="black", lw=1.2)
        ax.set_xlabel("Generación")
        ax.set_ylabel("f(x)")
        ax.set_xlim(0, max(1, self.num_gen))
        ax.grid(alpha=0.25)
        ax.legend(fontsize=7.5, loc="upper left", bbox_to_anchor=(1.01, 1))

    def crear_controles(self):
        self.slider = Slider(self.fig.add_axes([0.16, 0.075, 0.68, 0.03]), "Generación",
                             0, self.num_gen, valinit=0, valstep=1, color=AZUL)
        self.slider.on_changed(lambda v: self.actualizar(int(v)))
        botones = [("|<", lambda e: self.ir_a(0)),
                   ("<", lambda e: self.ir_a(self.gen - 1)),
                   ("Play / Pausa", lambda e: self.play_pausa()),
                   (">", lambda e: self.ir_a(self.gen + 1)),
                   (">|", lambda e: self.ir_a(self.num_gen))]
        self.botones, x = [], 0.25
        for texto, accion in botones:
            ancho = 0.16 if "Play" in texto else 0.07
            b = Button(self.fig.add_axes([x, 0.015, ancho, 0.045]), texto)
            b.on_clicked(accion)
            self.botones.append(b)
            x += ancho + 0.015
        self.timer = self.fig.canvas.new_timer(interval=150)
        self.timer.add_callback(self.paso_automatico)
        self.fig.canvas.mpl_connect("key_press_event", self.tecla)

    def ir_a(self, g):
        self.slider.set_val(int(np.clip(g, 0, self.num_gen)))

    def play_pausa(self):
        self.reproduciendo = not self.reproduciendo
        if self.reproduciendo:
            if self.gen >= self.num_gen:
                self.ir_a(0)
            self.timer.start()
        else:
            self.timer.stop()

    def paso_automatico(self):
        if self.gen >= self.num_gen:
            self.reproduciendo = False
            self.timer.stop()
        else:
            self.ir_a(self.gen + 1)

    def tecla(self, evento):
        if evento.key == "right":
            self.ir_a(self.gen + 1)
        elif evento.key == "left":
            self.ir_a(self.gen - 1)
        elif evento.key == " ":
            self.play_pausa()

    def actualizar(self, g):
        self.gen = g
        p, fv, im = self.h.poblaciones[g], self.h.valores[g], self.h.pos_mejor[g]
        if self.n == 1:
            self.puntos.set_offsets(np.column_stack([p[:, 0], fv]))
            self.estrella.set_data([p[im, 0]], [fv[im]])
        elif self.n == 2:
            self.puntos.set_offsets(p[:, :2])
            self.estrella.set_data([p[im, 0]], [p[im, 1]])
        else:
            cols = np.tile(np.arange(1, self.n + 1), len(p))
            jitter = (np.random.default_rng(g).random(len(cols)) - 0.5) * 0.3
            self.puntos.set_offsets(np.column_stack([cols + jitter, p.ravel()]))
            self.estrella.set_data(np.arange(1, self.n + 1), p[im])
        self.linea_gen.set_xdata([g, g])
        self.ax.set_title(f"Generación {g} de {self.num_gen}   |   mejor de la generación: "
                          f"f = {fv[im]:.6f}   |   media: {fv.mean():.4f}", fontsize=9.5)
        self.fig.canvas.draw_idle()

    def guardar_gif(self, archivo, fps=8):
        anim = FuncAnimation(self.fig, lambda g: self.actualizar(g),
                             frames=self.num_gen + 1, blit=False)
        anim.save(archivo, writer=PillowWriter(fps=fps))


def mostrar_graficas(hist, funcion, x_min, x_max, titulo, gif=None):
    if gif:
        vis = Visualizador(hist, funcion, x_min, x_max, titulo, interactivo=False)
        vis.guardar_gif(gif)
        print("Animacion guardada en", gif)
    else:
        vis = Visualizador(hist, funcion, x_min, x_max, titulo, interactivo=True)
        plt.show()

# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main(argv):
    # Si no se pasan parametros (por ejemplo al darle "Run" en el editor)
    # se usan estos valores de ejemplo
    if len(argv) < 8:
        print("Uso: python v3_varias_variables.py x_min x_max TOL tam_pob num_gen prob_cruce prob_mut")
        argv = [argv[0], "0.0", "100.0", "0.0001", "100", "100", "0.6", "0.05"]
        print("No se pasaron parametros; se usan:", " ".join(argv[1:]))
    gif = argv[argv.index("--gif") + 1] if "--gif" in argv else None

    # limites del intervalo en que se busca el optimo (los mismos para todas las variables)
    x_min = [float(argv[1])] * NUM_VAR
    x_max = [float(argv[2])] * NUM_VAR
    TOL = float(argv[3])          # tolerancia o exactitud con que se busca el optimo
    tam_pob = int(argv[4])        # tamano de la poblacion
    num_gen = int(argv[5])        # numero de iteraciones
    prob_cruce = float(argv[6])   # porcentaje de cruces
    prob_mut = float(argv[7])     # porcentaje de mutaciones
    cmax = 0.0

    # inicializaciones: longitud del cromosoma de cada variable
    lcrom = []
    for i in range(NUM_VAR):
        lcrom.append(int(math.ceil(math.log(1 + (x_max[i] - x_min[i]) / TOL) / math.log(2.0))))

    # inicializacion de numeros aleatorios
    random.seed(time.time())

    # se genera la poblacion inicial
    pob = poblacion_inicial(tam_pob, lcrom, x_min, x_max)
    # transformacion de la adaptacion para minimizar
    cmax = revisar_adap_mini(pob, tam_pob, lcrom, cmax, x_min, x_max)
    # se evalua la poblacion
    pos_mejor = 0
    pos_mejor, sumaptitud = evaluacion(pob, tam_pob, pos_mejor)

    # HISTORIAL (agregado)
    hist = Historial(maximizar=False)
    hist.registrar([ind.vec_x for ind in pob], [ind.aptitud_bruta for ind in pob], pos_mejor)

    # bucle de evolucion
    for generacion in range(num_gen):
        seleccion(pob, tam_pob)
        reproduccion(pob, tam_pob, lcrom, prob_cruce, x_min, x_max)
        mutacion(pob, tam_pob, lcrom, prob_mut, x_min, x_max)
        cmax = revisar_adap_mini(pob, tam_pob, lcrom, cmax, x_min, x_max)
        pos_mejor, sumaptitud = evaluacion(pob, tam_pob, pos_mejor)
        # HISTORIAL (agregado)
        hist.registrar([ind.vec_x for ind in pob], [ind.aptitud_bruta for ind in pob], pos_mejor)

    print("Aptitud del mejor(" + str(pos_mejor) + ") = ", end="")
    print(pob[pos_mejor].aptitud_bruta, end="")
    print(" en ", pob[pos_mejor].vec_x)

    # GRAFICAS (agregado)
    mostrar_graficas(hist, funcion, x_min, x_max,
                     f"Proyecto 1 - v3 Varias variables (n={NUM_VAR}): f = Σ -x_i sen(√|x_i|)", gif)


if __name__ == "__main__":
    main(sys.argv)
