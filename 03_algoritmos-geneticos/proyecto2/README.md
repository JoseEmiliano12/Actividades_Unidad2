# Proyecto 2: cromosomas reales

Implementación en Python del algoritmo genético con genes reales. Este proyecto muestra resultados **numéricos**, sin gráficas. No usa DEAP ni paquetes externos.

## Ejecutar

```bash
cd '/home/emiliano/Documentos/FUNDAMENTOS DE INTELIGENCIA ARTIFICIAL/Tareaalgortimosgenericos/proyecto2'
python3 proyecto2.py
```

Por defecto resuelve Schwefel con 3 variables y **abre una ventana con una tabla visual** de todas las generaciones. También muestra un resumen en la terminal y crea `tabla_resultados.html` para el navegador y `tabla_resultados.csv` para una hoja de cálculo. Ninguna vista contiene gráficas. Cada nueva ejecución actualiza ambas tablas.

Si ejecutas el programa en un entorno sin pantalla o solo quieres la salida de terminal, usa `python3 proyecto2.py --consola`.

Para comprobar que el código compila como Python:

```bash
python3 -m py_compile algoritmo.py proyecto2.py
```

## Ejemplos

```bash
python3 proyecto2.py --funcion max1
python3 proyecto2.py --funcion max2 --operador aritmetico
python3 proyecto2.py --funcion min1
python3 proyecto2.py --funcion rastrigin --n 10 --operador un_punto
python3 proyecto2.py --funcion schwefel --n 3 --generaciones 300 --poblacion 100
```

Opciones: `--funcion`, `--n`, `--poblacion`, `--generaciones`, `--cruce`, `--mutacion`, `--operador`, `--semilla`, `--sin-elitismo`, `--cada` y `--consola`. Cruce y mutación se expresan como probabilidades entre 0 y 1. El cruce de un punto requiere al menos dos variables. La semilla permite repetir una corrida.

El archivo `algoritmo.py` contiene la representación real, selección por ruleta, cruces de un punto, uniforme, aritmético y SBX, mutación uniforme y elitismo opcional. El archivo `proyecto2.py` es la interfaz de línea de comandos.
