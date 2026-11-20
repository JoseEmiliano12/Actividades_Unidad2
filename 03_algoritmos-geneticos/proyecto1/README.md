# Proyecto 1: funciones 1 y 2

Implementación en Python de un algoritmo genético binario para **las dos funciones de maximización acordadas**. No usa DEAP ni paquetes externos.

## Ver la visualización

Abre `visualizacion.html` con doble clic. Puedes elegir la función 1 o 2, ir al inicio o al final, avanzar o retroceder una generación, reproducir la evolución y seleccionar un punto para seguir su trayectoria. La gráfica «Evolución del resultado» compara el mejor de cada generación, la media y el mejor acumulado. Usa las flechas izquierda/derecha, Inicio/Fin y Espacio como atajos. Cada color de la gráfica de movimiento identifica una posición de la población; al crear descendientes, esa posición puede pasar a otro individuo.

## Ajustar parámetros y volver a simular

```bash
cd '/home/emiliano/Documentos/FUNDAMENTOS DE INTELIGENCIA ARTIFICIAL/Tareaalgortimosgenericos/proyecto1'
python3 proyecto1.py
```

La aplicación Tkinter permite elegir función, población, generaciones, probabilidad de cruce, probabilidad de mutación, semilla y elitismo. Incluye la gráfica de evolución y la de movimiento en pestañas, además de los mismos controles de navegación. Usa selección por ruleta, cruce de un punto y mutación bit a bit.

Para comprobar sin abrir la ventana: `python3 proyecto1.py --verificar`. Si cambias los valores por defecto, `python3 exportar.py` regenera `visualizacion.html`.
