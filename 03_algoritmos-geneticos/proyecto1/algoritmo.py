"""Algoritmo genético binario para las dos primeras funciones del Proyecto 1."""
from __future__ import annotations

from dataclasses import dataclass
import math
import random


@dataclass(frozen=True)
class Funcion:
    nombre: str
    minimo: float
    maximo: float
    optimo_x: float
    optimo_y: float

    def evaluar(self, x: float) -> float:
        if self.nombre == "Función 1":
            return math.sin(5 * math.pi * x) ** 6 * math.exp(
                -2 * math.log(2) * ((x - 0.1) / 0.8) ** 2
            )
        return 20 + math.e - 20 * math.exp(-0.2 * abs(x)) - math.exp(
            math.cos(2 * math.pi * x)
        )


FUNCIONES = (
    Funcion("Función 1", 0.0, 1.0, 0.1, 1.0),
    Funcion("Función 2", 0.0, 32.0, 31.5005, 22.3136),
)


@dataclass(frozen=True)
class Configuracion:
    poblacion: int = 24
    generaciones: int = 60
    cruce: float = 0.8
    mutacion: float = 0.01
    bits: int = 18
    elitismo: bool = True
    semilla: int = 2

    def validar(self) -> None:
        if not 2 <= self.poblacion <= 150:
            raise ValueError("La población debe estar entre 2 y 150.")
        if not 1 <= self.generaciones <= 500:
            raise ValueError("Las generaciones deben estar entre 1 y 500.")
        if not 0 <= self.cruce <= 1 or not 0 <= self.mutacion <= 1:
            raise ValueError("Cruce y mutación deben ser probabilidades entre 0 y 1.")
        if not 2 <= self.bits <= 30:
            raise ValueError("Los bits deben estar entre 2 y 30.")


@dataclass(frozen=True)
class Individuo:
    cromosoma: int
    x: float
    aptitud: float


def resumen_generaciones(historia: list[list[Individuo]]) -> list[tuple[float, float, float]]:
    """Mejor de la generación, media y mejor acumulado, en ese orden."""
    resumen = []
    mejor_acumulado = float("-inf")
    for poblacion in historia:
        mejor = max(ind.aptitud for ind in poblacion)
        media = sum(ind.aptitud for ind in poblacion) / len(poblacion)
        mejor_acumulado = max(mejor_acumulado, mejor)
        resumen.append((mejor, media, mejor_acumulado))
    return resumen


def ejecutar(funcion: Funcion, cfg: Configuracion) -> list[list[Individuo]]:
    """Devuelve una población por generación, incluyendo la generación inicial."""
    cfg.validar()
    rng = random.Random(cfg.semilla)
    mascara = (1 << cfg.bits) - 1

    def crear(cromosoma: int) -> Individuo:
        x = funcion.minimo + (funcion.maximo - funcion.minimo) * cromosoma / mascara
        return Individuo(cromosoma, x, funcion.evaluar(x))

    def seleccionar(poblacion: list[Individuo]) -> Individuo:
        minimo = min(ind.aptitud for ind in poblacion)
        pesos = [ind.aptitud - minimo + 1e-12 for ind in poblacion]
        return rng.choices(poblacion, weights=pesos, k=1)[0]

    def cruzar(a: int, b: int) -> tuple[int, int]:
        if rng.random() >= cfg.cruce:
            return a, b
        punto = rng.randrange(1, cfg.bits)
        parte_baja = (1 << punto) - 1
        return ((a & ~parte_baja) | (b & parte_baja),
                (b & ~parte_baja) | (a & parte_baja))

    def mutar(cromosoma: int) -> int:
        for bit in range(cfg.bits):
            if rng.random() < cfg.mutacion:
                cromosoma ^= 1 << bit
        return cromosoma

    poblacion = [crear(rng.randrange(mascara + 1)) for _ in range(cfg.poblacion)]
    historia = [poblacion]
    for _ in range(cfg.generaciones):
        siguiente = []
        if cfg.elitismo:
            siguiente.append(max(poblacion, key=lambda ind: ind.aptitud))
        while len(siguiente) < cfg.poblacion:
            padre1, padre2 = seleccionar(poblacion), seleccionar(poblacion)
            hijo1, hijo2 = cruzar(padre1.cromosoma, padre2.cromosoma)
            for cromosoma in (hijo1, hijo2):
                if len(siguiente) < cfg.poblacion:
                    siguiente.append(crear(mutar(cromosoma)))
        poblacion = siguiente
        historia.append(poblacion)
    return historia
