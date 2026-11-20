# Proyecto completo de algoritmos genéticos

Esta carpeta reúne los dos proyectos de la materia **Fundamentos de Inteligencia Artificial**. Es una copia nueva; los originales permanecen en `Tareaalgortimosgenericos`.

## Qué contiene

| Carpeta | Contenido principal | Cómo verlo |
|---|---|---|
| `proyecto1/` | Algoritmo genético binario para dos funciones de maximización. | `proyecto1/visualizacion.html` o la aplicación `proyecto1/proyecto1.py`. |
| `proyecto2/` | Algoritmo genético con cromosomas de genes reales y distintas funciones. | `proyecto2/proyecto2.py`; genera tablas HTML y CSV. |

`proyecto1/` también conserva subcarpetas con versiones y animaciones adicionales. Los programas principales para entregar o demostrar son los indicados en la tabla. Los archivos `README.md` dentro de cada proyecto explican sus parámetros y ejemplos.

## Ejecución rápida

Desde esta carpeta:

```bash
./ejecutar.sh binario
./ejecutar.sh real
```

Para abrir la visualización HTML del proyecto binario, abre `proyecto1/visualizacion.html` con doble clic. No necesita instalar paquetes.

También puedes ejecutar directamente:

```bash
python3 proyecto1/proyecto1.py
python3 proyecto2/proyecto2.py
```

Para usar el proyecto de genes reales solo en consola:

```bash
python3 proyecto2/proyecto2.py --consola
```

Ambos programas principales usan la biblioteca estándar de Python. Algunos **ejemplos adicionales** de las subcarpetas requieren NumPy, Matplotlib o PySide6 y pueden tener entradas experimentales; no son necesarios para ejecutar `proyecto1.py` o `proyecto2.py`.

## Comprobación

```bash
python3 proyecto1/proyecto1.py --verificar
python3 -m py_compile proyecto1/algoritmo.py proyecto1/proyecto1.py proyecto2/algoritmo.py proyecto2/proyecto2.py
```

`proyecto2.py` actualiza `tabla_resultados.html` y `tabla_resultados.csv` cada vez que se ejecuta. La carpeta incluye una copia de las tablas existentes antes de crear este paquete.
