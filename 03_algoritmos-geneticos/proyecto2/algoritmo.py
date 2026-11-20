"""Algoritmo genético con cromosomas reales para el Proyecto 2."""
from __future__ import annotations

from dataclasses import dataclass
import math
import random


@dataclass(frozen=True)
class Funcion:
    clave: str
    nombre: str
    limites: tuple[tuple[float, float], ...]
    objetivo: str  # "max" o "min"
    referencia: str

    def evaluar(self, genes: tuple[float, ...]) -> float:
        if len(genes) != len(self.limites):
            raise ValueError("La cantidad de genes no coincide con la función.")
        if self.clave == "max1":
            x = genes[0]
            return math.sin(5 * math.pi * x) ** 6 * math.exp(
                -2 * math.log(2) * ((x - 0.1) / 0.8) ** 2
            )
        if self.clave == "max2":
            x = genes[0]
            return 20 + math.e - 20 * math.exp(-0.2 * abs(x)) - math.exp(
                math.cos(2 * math.pi * x)
            )
        if self.clave == "min1":
            x = genes[0]
            return -abs(x * math.sin(math.sqrt(abs(x))))
        if self.clave == "rastrigin":
            return 10 * len(genes) + sum(
                x * x - 10 * math.cos(2 * math.pi * x) for x in genes
            )
        if self.clave == "schwefel":
            return -sum(x * math.sin(math.sqrt(abs(x))) for x in genes)
        raise ValueError(f"Función desconocida: {self.clave}")

    def puntuacion(self, valor: float) -> float:
        return valor if self.objetivo == "max" else -valor


def crear_funcion(clave: str, n: int = 3) -> Funcion:
    if not 1 <= n <= 20:
        raise ValueError("n debe estar entre 1 y 20.")
    catalogo = {
        "max1": Funcion("max1", "Máximo: función 1", ((0.0, 1.0),), "max", "f(0.1) = 1"),
        "max2": Funcion("max2", "Máximo: función 2", ((0.0, 32.0),), "max", "f(31.5005) ≈ 22.3136"),
        "min1": Funcion("min1", "Mínimo: función escalar", ((-250.0, 250.0),), "min", "f(203.814) ≈ -201.843"),
        "rastrigin": Funcion("rastrigin", f"Rastrigin ({n} variables)", ((-5.12, 5.12),) * n, "min", "f(0,…,0) = 0"),
        "schwefel": Funcion("schwefel", f"Schwefel ({n} variables)", ((0.0, 100.0),) * n, "min", f"f(65.54785,…,65.54785) ≈ {-n * 63.63498:.5f}"),
    }
    if clave not in catalogo:
        raise ValueError(f"Función desconocida: {clave}")
    return catalogo[clave]


@dataclass(frozen=True)
class Configuracion:
    poblacion: int = 60
    generaciones: int = 150
    cruce: float = 0.8
    mutacion: float = 0.03
    elitismo: bool = True
    semilla: int = 8
    operador: str = "sbx"  # sbx, aritmetico, uniforme, un_punto

    def validar(self) -> None:
        if not 2 <= self.poblacion <= 1000:
            raise ValueError("La población debe estar entre 2 y 1000.")
        if not 1 <= self.generaciones <= 10000:
            raise ValueError("Las generaciones deben estar entre 1 y 10000.")
        if not 0 <= self.cruce <= 1 or not 0 <= self.mutacion <= 1:
            raise ValueError("Cruce y mutación deben estar entre 0 y 1.")
        if self.operador not in ("sbx", "aritmetico", "uniforme", "un_punto"):
            raise ValueError("Operador desconocido.")


@dataclass(frozen=True)
class Individuo:
    genes: tuple[float, ...]
    valor: float


def ejecutar(funcion: Funcion, cfg: Configuracion) -> list[list[Individuo]]:
    """Evoluciona cromosomas reales y devuelve la historia completa."""
    cfg.validar()
    if cfg.operador == "un_punto" and len(funcion.limites) == 1:
        raise ValueError("El cruce de un punto requiere al menos dos variables.")
    rng = random.Random(cfg.semilla)
    n = len(funcion.limites)

    def crear(genes: tuple[float, ...]) -> Individuo:
        recortados = tuple(max(inf, min(sup, x)) for x, (inf, sup) in zip(genes, funcion.limites))
        return Individuo(recortados, funcion.evaluar(recortados))

    def aleatorio() -> Individuo:
        return crear(tuple(rng.uniform(inf, sup) for inf, sup in funcion.limites))

    def seleccionar(poblacion: list[Individuo]) -> Individuo:
        puntajes = [funcion.puntuacion(ind.valor) for ind in poblacion]
        minimo = min(puntajes)
        pesos = [p - minimo + 1e-12 for p in puntajes]
        return rng.choices(poblacion, weights=pesos, k=1)[0]

    def cruzar(a: tuple[float, ...], b: tuple[float, ...]) -> tuple[tuple[float, ...], tuple[float, ...]]:
        if rng.random() >= cfg.cruce:
            return a, b
        if cfg.operador == "un_punto":
            punto = rng.randrange(1, n)
            return a[:punto] + b[punto:], b[:punto] + a[punto:]
        h1, h2 = [], []
        for x, y in zip(a, b):
            if cfg.operador == "uniforme":
                v, w = (y, x) if rng.random() < 0.5 else (x, y)
            elif cfg.operador == "aritmetico":
                alfa = rng.random()
                v, w = alfa * x + (1 - alfa) * y, alfa * y + (1 - alfa) * x
            else:  # SBX con índice de distribución eta=1.
                u = rng.random()
                beta = (2 * u) ** 0.5 if u <= 0.5 else (1 / (2 * (1 - u))) ** 0.5
                v = 0.5 * ((x + y) - beta * (y - x))
                w = 0.5 * ((x + y) + beta * (y - x))
            h1.append(v)
            h2.append(w)
        return tuple(h1), tuple(h2)

    def mutar(genes: tuple[float, ...]) -> tuple[float, ...]:
        return tuple(rng.uniform(inf, sup) if rng.random() < cfg.mutacion else x
                     for x, (inf, sup) in zip(genes, funcion.limites))

    poblacion = [aleatorio() for _ in range(cfg.poblacion)]
    historia = [poblacion]
    for _ in range(cfg.generaciones):
        siguiente = []
        if cfg.elitismo:
            siguiente.append(max(poblacion, key=lambda ind: funcion.puntuacion(ind.valor)))
        while len(siguiente) < cfg.poblacion:
            padre1, padre2 = seleccionar(poblacion), seleccionar(poblacion)
            for genes in cruzar(padre1.genes, padre2.genes):
                if len(siguiente) < cfg.poblacion:
                    siguiente.append(crear(mutar(genes)))
        poblacion = siguiente
        historia.append(poblacion)
    return historia


def mejor(poblacion: list[Individuo], funcion: Funcion) -> Individuo:
    return max(poblacion, key=lambda ind: funcion.puntuacion(ind.valor))
