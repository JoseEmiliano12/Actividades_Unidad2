"""Interfaz para observar, paso a paso, la evolución de la población."""
from __future__ import annotations

import argparse
import colorsys
import tkinter as tk
from tkinter import messagebox, ttk

from algoritmo import Configuracion, FUNCIONES, ejecutar, resumen_generaciones


def color_individuo(i: int, total: int) -> str:
    r, g, b = colorsys.hsv_to_rgb(i / max(total, 1), 0.72, 0.83)
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"


class Aplicacion:
    def __init__(self, raiz: tk.Tk) -> None:
        self.raiz = raiz
        self.raiz.title("Proyecto 1 · Algoritmo genético binario")
        self.raiz.geometry("1120x880")
        self.raiz.minsize(820, 680)
        self.raiz.configure(bg="#eef3f8")
        self.funcion_var = tk.StringVar(value=FUNCIONES[0].nombre)
        self.poblacion_var = tk.StringVar(value="24")
        self.generaciones_var = tk.StringVar(value="60")
        self.cruce_var = tk.StringVar(value="0.8")
        self.mutacion_var = tk.StringVar(value="0.01")
        self.semilla_var = tk.StringVar(value="2")
        self.elitismo_var = tk.BooleanVar(value=True)
        self.velocidad_var = tk.IntVar(value=250)
        self.generacion_var = tk.IntVar(value=0)
        self.estado_var = tk.StringVar(value="")
        self.seleccionado: int | None = None
        self.historia = []
        self.generacion = 0
        self.en_reproduccion = False
        self.animacion = 0.0
        self.temporizador: str | None = None
        self._construir()
        self.simular()
        for tecla, accion in (("<Left>", self.anterior), ("<Right>", self.siguiente),
                              ("<Home>", self.inicio), ("<End>", self.final),
                              ("<space>", self.alternar_reproduccion)):
            self.raiz.bind(tecla, lambda _evento, accion=accion: self._atajo(accion))

    def _construir(self) -> None:
        estilo = ttk.Style()
        if "clam" in estilo.theme_names():
            estilo.theme_use("clam")
        estilo.configure("TFrame", background="#eef3f8")
        estilo.configure("TLabel", background="#eef3f8", foreground="#17283c", font=("Sans", 10))
        estilo.configure("TButton", padding=(12, 8), font=("Sans", 10, "bold"))
        estilo.configure("Accent.TButton", background="#136781", foreground="white", padding=(13, 8), font=("Sans", 10, "bold"))
        estilo.map("Accent.TButton", background=[("active", "#0b526a")])
        estilo.configure("TEntry", padding=5)
        estilo.configure("TCombobox", padding=5)
        estilo.configure("Estado.TLabel", font=("Sans", 11, "bold"), foreground="#17465c")
        cont = ttk.Frame(self.raiz, padding=16)
        cont.pack(fill="both", expand=True)
        cabecera = tk.Frame(cont, bg="#155775", padx=22, pady=18)
        cabecera.pack(fill="x", pady=(0, 15))
        tk.Label(cabecera, text="PROYECTO 1 · SIMULACIÓN INTERACTIVA", bg="#155775", fg="#9ee4ee",
                 font=("Sans", 9, "bold")).pack(anchor="w")
        tk.Label(cabecera, text="Optimización de funciones", bg="#155775", fg="white",
                 font=("Sans", 20, "bold")).pack(anchor="w", pady=(3, 2))
        tk.Label(cabecera, text="Observa cómo cambia la población en cada generación.",
                 bg="#155775", fg="#d9edf5", font=("Sans", 10)).pack(anchor="w")

        config = ttk.Frame(cont)
        config.pack(fill="x", pady=(0, 8))
        campos = [
            ("Función", self.funcion_var, [f.nombre for f in FUNCIONES], 18),
            ("Población", self.poblacion_var, None, 7),
            ("Generaciones", self.generaciones_var, None, 8),
            ("Cruce", self.cruce_var, None, 6),
            ("Mutación", self.mutacion_var, None, 7),
            ("Semilla", self.semilla_var, None, 7),
        ]
        for columna, (etiqueta, variable, opciones, ancho) in enumerate(campos):
            marco = ttk.Frame(config)
            marco.grid(row=0, column=columna, padx=(0, 9), sticky="w")
            ttk.Label(marco, text=etiqueta).pack(anchor="w")
            if opciones:
                ttk.Combobox(marco, textvariable=variable, values=opciones,
                             state="readonly", width=ancho).pack()
            else:
                ttk.Entry(marco, textvariable=variable, width=ancho).pack()
        ttk.Checkbutton(config, text="Elitismo", variable=self.elitismo_var).grid(row=0, column=6, padx=4, sticky="s")
        ttk.Button(config, text="Nueva simulación", style="Accent.TButton", command=self.simular).grid(row=0, column=7, padx=5, sticky="s")

        ttk.Label(cont, text="POBLACIÓN SOBRE LA FUNCIÓN", style="Estado.TLabel").pack(anchor="w", pady=(4, 6))
        self.grafica = tk.Canvas(cont, bg="white", highlightthickness=1,
                                 highlightbackground="#dce5ef", height=380)
        self.grafica.pack(fill="both", expand=True)
        self.grafica.bind("<Configure>", lambda _e: self.dibujar())
        self.grafica.bind("<Button-1>", self.elegir_punto)

        ttk.Label(cont, textvariable=self.estado_var, style="Estado.TLabel").pack(anchor="w", pady=(8, 5))
        controles = ttk.Frame(cont)
        controles.pack(fill="x", pady=(0, 7))
        ttk.Button(controles, text="|◀ Inicio", command=self.inicio).pack(side="left", padx=(0, 5))
        ttk.Button(controles, text="◀ Anterior", command=self.anterior).pack(side="left", padx=(0, 5))
        ttk.Button(controles, text="Siguiente ▶", command=self.siguiente).pack(side="left", padx=(0, 5))
        ttk.Button(controles, text="Final ▶|", command=self.final).pack(side="left", padx=(0, 5))
        self.boton_reproducir = ttk.Button(controles, text="▶ Reproducir", style="Accent.TButton", command=self.alternar_reproduccion)
        self.boton_reproducir.pack(side="left", padx=(0, 10))
        self.deslizador = ttk.Scale(controles, from_=0, to=60, orient="horizontal",
                                    command=self.ir_a_generacion)
        self.deslizador.pack(side="left", fill="x", expand=True, padx=(0, 9))
        ttk.Label(controles, text="ms/generación").pack(side="left")
        ttk.Spinbox(controles, from_=80, to=2000, increment=50,
                    textvariable=self.velocidad_var, width=6).pack(side="left", padx=(4, 0))
        pestanas = ttk.Notebook(cont)
        pestanas.pack(fill="both", expand=True, pady=(6, 0))
        marco_evolucion = tk.Frame(pestanas, bg="white")
        marco_trayectorias = tk.Frame(pestanas, bg="white")
        pestanas.add(marco_evolucion, text="Evolución del resultado")
        pestanas.add(marco_trayectorias, text="Movimiento de individuos")
        tk.Label(marco_evolucion, text="Azul: mejor acumulado    Naranja: mejor de la generación    Gris: media",
                 bg="white", fg="#526174", font=("Sans", 10)).pack(anchor="w", padx=12, pady=(8, 0))
        self.evolucion_canvas = tk.Canvas(marco_evolucion, bg="white", highlightthickness=0, height=200)
        self.evolucion_canvas.pack(fill="both", expand=True)
        self.evolucion_canvas.bind("<Configure>", lambda _e: self.dibujar_evolucion())
        tk.Label(marco_trayectorias, text="Cada color indica una posición; los descendientes pueden ocuparla en la siguiente generación.",
                 bg="white", fg="#526174", font=("Sans", 10)).pack(anchor="w", padx=12, pady=(8, 0))
        self.trayectorias = tk.Canvas(marco_trayectorias, bg="white", highlightthickness=0, height=200)
        self.trayectorias.pack(fill="both", expand=True)
        self.trayectorias.bind("<Configure>", lambda _e: self.dibujar_trayectorias())
        pestanas.bind("<<NotebookTabChanged>>", lambda _e: (self.dibujar_evolucion(), self.dibujar_trayectorias()))

    def simular(self) -> None:
        self.pausar()
        try:
            cfg = Configuracion(
                poblacion=int(self.poblacion_var.get()),
                generaciones=int(self.generaciones_var.get()),
                cruce=float(self.cruce_var.get()),
                mutacion=float(self.mutacion_var.get()),
                elitismo=self.elitismo_var.get(),
                semilla=int(self.semilla_var.get()),
            )
            funcion = next(f for f in FUNCIONES if f.nombre == self.funcion_var.get())
            historia = ejecutar(funcion, cfg)
        except (ValueError, StopIteration) as error:
            messagebox.showerror("Parámetros inválidos", str(error))
            return
        self.funcion, self.cfg, self.historia = funcion, cfg, historia
        self.evolucion = resumen_generaciones(historia)
        self.generacion = 0
        self.animacion = 0.0
        self.seleccionado = None
        self.deslizador.configure(to=cfg.generaciones)
        self.deslizador.set(0)
        self.dibujar()

    def ir_a_generacion(self, valor: str) -> None:
        if not self.historia:
            return
        objetivo = round(float(valor))
        if objetivo != self.generacion:
            self.pausar()
            self.generacion = max(0, min(objetivo, len(self.historia) - 1))
            self.animacion = 0.0
            self.dibujar()

    def anterior(self) -> None:
        self.pausar()
        self.generacion = max(0, self.generacion - 1)
        self.animacion = 0.0
        self.deslizador.set(self.generacion)
        self.dibujar()

    def inicio(self) -> None:
        self.pausar()
        self.generacion = 0
        self.animacion = 0.0
        self.deslizador.set(0)
        self.dibujar()

    def siguiente(self) -> None:
        self.pausar()
        self.generacion = min(len(self.historia) - 1, self.generacion + 1)
        self.animacion = 0.0
        self.deslizador.set(self.generacion)
        self.dibujar()

    def final(self) -> None:
        self.pausar()
        self.generacion = len(self.historia) - 1
        self.animacion = 0.0
        self.deslizador.set(self.generacion)
        self.dibujar()

    def _atajo(self, accion) -> None:
        foco = self.raiz.focus_get()
        if foco is not None and foco.winfo_class() in {"Entry", "TEntry", "TCombobox", "Spinbox", "TSpinbox", "Button", "TButton"}:
            return
        accion()

    def alternar_reproduccion(self) -> None:
        if self.en_reproduccion:
            self.pausar()
        else:
            if self.generacion >= len(self.historia) - 1:
                self.generacion = 0
                self.deslizador.set(0)
            self.en_reproduccion = True
            self.boton_reproducir.configure(text="⏸ Pausar")
            self._cuadro()

    def pausar(self) -> None:
        self.en_reproduccion = False
        if self.temporizador is not None:
            self.raiz.after_cancel(self.temporizador)
            self.temporizador = None
        if hasattr(self, "boton_reproducir"):
            self.boton_reproducir.configure(text="▶ Reproducir")

    def _cuadro(self) -> None:
        if not self.en_reproduccion:
            return
        if self.generacion >= len(self.historia) - 1:
            self.pausar()
            return
        self.animacion += 0.1
        if self.animacion >= 1:
            self.generacion += 1
            self.animacion = 0.0
            self.deslizador.set(self.generacion)
        self.dibujar()
        demora = max(8, int(self.velocidad_var.get()) // 10)
        self.temporizador = self.raiz.after(demora, self._cuadro)

    def _medidas(self):
        w = max(450, self.grafica.winfo_width())
        h = max(250, self.grafica.winfo_height())
        izquierda, derecha, arriba, abajo = 65, w - 25, 28, h - 48
        muestras = [self.funcion.evaluar(self.funcion.minimo +
                    (self.funcion.maximo - self.funcion.minimo) * i / 699)
                    for i in range(700)]
        y_min, y_max = min(muestras), max(muestras)
        margen = max((y_max - y_min) * 0.10, 0.05)
        y_min -= margen
        y_max += margen
        def punto(x, y):
            px = izquierda + (x - self.funcion.minimo) / (self.funcion.maximo - self.funcion.minimo) * (derecha - izquierda)
            py = abajo - (y - y_min) / (y_max - y_min) * (abajo - arriba)
            return px, py
        return izquierda, derecha, arriba, abajo, y_min, y_max, punto, muestras

    def dibujar(self) -> None:
        if not self.historia:
            return
        c = self.grafica
        c.delete("all")
        izq, der, arr, aba, y_min, y_max, punto, muestras = self._medidas()
        for j in range(5):
            y = arr + j * (aba - arr) / 4
            valor = y_max - j * (y_max - y_min) / 4
            c.create_line(izq, y, der, y, fill="#e9edf3")
            c.create_text(izq - 8, y, text=f"{valor:.2f}", anchor="e", fill="#526174")
        for j in range(5):
            x = izq + j * (der - izq) / 4
            valor = self.funcion.minimo + j * (self.funcion.maximo - self.funcion.minimo) / 4
            c.create_line(x, arr, x, aba, fill="#e9edf3")
            c.create_text(x, aba + 16, text=f"{valor:.2f}", fill="#526174")
        coords = []
        for i, y in enumerate(muestras):
            x = self.funcion.minimo + (self.funcion.maximo - self.funcion.minimo) * i / 699
            coords.extend(punto(x, y))
        c.create_line(*coords, fill="#28518c", width=2, smooth=False)
        ox, oy = punto(self.funcion.optimo_x, self.funcion.optimo_y)
        c.create_text(ox, oy - 16, text="★ óptimo", fill="#b45309", font=("Sans", 10, "bold"))
        c.create_oval(ox - 5, oy - 5, ox + 5, oy + 5, outline="#b45309", width=2)
        actual = self.historia[self.generacion]
        anterior = self.historia[self.generacion - 1] if self.generacion > 0 else actual
        proxima = self.historia[self.generacion + 1] if self.generacion < len(self.historia) - 1 else actual
        puntos = []
        for i, ind in enumerate(actual):
            color = color_individuo(i, len(actual))
            x, y = punto(ind.x, ind.aptitud)
            if self.animacion > 0 and self.generacion < len(self.historia) - 1:
                nx, ny = punto(proxima[i].x, proxima[i].aptitud)
                c.create_line(x, y, nx, ny, fill=color, width=1, dash=(3, 3))
                x += (nx - x) * self.animacion
                y += (ny - y) * self.animacion
            elif self.generacion > 0:
                px, py = punto(anterior[i].x, anterior[i].aptitud)
                c.create_line(px, py, x, y, fill=color, width=1, dash=(3, 3))
            puntos.append((x, y))
        for i, (x, y) in enumerate(puntos):
            radio = 7 if i == self.seleccionado else 4
            c.create_oval(x - radio, y - radio, x + radio, y + radio,
                          fill=color_individuo(i, len(actual)),
                          outline="#0f172a" if i == self.seleccionado else "white",
                          width=2 if i == self.seleccionado else 1,
                          tags=(f"individuo:{i}",))
        mejor = max(actual, key=lambda ind: ind.aptitud)
        mx, my = punto(mejor.x, mejor.aptitud)
        c.create_text(mx, my + 16, text="★ mejor", fill="#173d58", font=("Sans", 10, "bold"))
        media = sum(ind.aptitud for ind in actual) / len(actual)
        detalle = ""
        if self.seleccionado is not None and self.seleccionado < len(actual):
            ind = actual[self.seleccionado]
            detalle = f"  ·  Punto {self.seleccionado + 1}: x={ind.x:.5f}, f(x)={ind.aptitud:.5f}"
        acumulado = self.evolucion[self.generacion][2]
        self.estado_var.set(f"Generación {self.generacion}/{self.cfg.generaciones}  ·  Mejor: x={mejor.x:.5f}, f(x)={mejor.aptitud:.5f}  ·  Media={media:.5f}  ·  Mejor acumulado={acumulado:.5f}{detalle}")
        self.dibujar_evolucion()
        self.dibujar_trayectorias()

    def dibujar_evolucion(self) -> None:
        if not self.historia:
            return
        c = self.evolucion_canvas
        c.delete("all")
        w, h = max(450, c.winfo_width()), max(150, c.winfo_height())
        izq, der, arr, aba = 65, w - 25, 18, h - 32
        valores = [valor for fila in self.evolucion for valor in fila]
        minimo, maximo = min(valores), max(valores)
        margen = max((maximo - minimo) * 0.08, 0.05)
        minimo -= margen
        maximo += margen
        total = len(self.evolucion) - 1

        def punto(g: int, valor: float) -> tuple[float, float]:
            return (izq + g / max(total, 1) * (der - izq),
                    aba - (valor - minimo) / (maximo - minimo) * (aba - arr))

        for j in range(5):
            y = arr + j * (aba - arr) / 4
            c.create_line(izq, y, der, y, fill="#e9edf3")
            c.create_text(izq - 7, y, text=f"{maximo - j * (maximo - minimo) / 4:.2f}",
                          anchor="e", fill="#526174")
            x = izq + j * (der - izq) / 4
            c.create_line(x, arr, x, aba, fill="#e9edf3")
            c.create_text(x, aba + 15, text=str(round(j * total / 4)), fill="#526174")
        c.create_text((izq + der) / 2, h - 8, text="Generación", fill="#526174")
        for columna, color, ancho in ((2, "#28518c", 3), (0, "#df7842", 2), (1, "#7c8b99", 2)):
            coords = []
            for g, fila in enumerate(self.evolucion):
                coords.extend(punto(g, fila[columna]))
            if len(coords) >= 4:
                c.create_line(*coords, fill=color, width=ancho)
            x, y = punto(self.generacion, self.evolucion[self.generacion][columna])
            c.create_oval(x - 4, y - 4, x + 4, y + 4, fill=color, outline="white")
        x, _ = punto(self.generacion, minimo)
        c.create_line(x, arr, x, aba, fill="#334155", dash=(4, 3))

    def elegir_punto(self, evento) -> None:
        if not self.historia:
            return
        elemento = self.grafica.find_closest(evento.x, evento.y)
        if not elemento:
            return
        for etiqueta in self.grafica.gettags(elemento[0]):
            if etiqueta.startswith("individuo:"):
                self.seleccionado = int(etiqueta.split(":")[1])
                self.dibujar()
                return

    def dibujar_trayectorias(self) -> None:
        if not self.historia:
            return
        c = self.trayectorias
        c.delete("all")
        w, h = max(450, c.winfo_width()), max(150, c.winfo_height())
        izq, der, arr, aba = 60, w - 25, 15, h - 30
        total = len(self.historia) - 1
        def punto(g, x):
            px = izq + g / max(total, 1) * (der - izq)
            py = aba - (x - self.funcion.minimo) / (self.funcion.maximo - self.funcion.minimo) * (aba - arr)
            return px, py
        for j in range(5):
            y = arr + j * (aba - arr) / 4
            valor = self.funcion.maximo - j * (self.funcion.maximo - self.funcion.minimo) / 4
            c.create_line(izq, y, der, y, fill="#edf1f5")
            c.create_text(izq - 7, y, text=f"{valor:.1f}", anchor="e", fill="#526174")
        c.create_text((izq + der) / 2, h - 9, text="Generación", fill="#526174")
        for i in range(len(self.historia[0])):
            coords = []
            for g in range(self.generacion + 1):
                coords.extend(punto(g, self.historia[g][i].x))
            color = color_individuo(i, len(self.historia[0]))
            if len(coords) >= 4:
                c.create_line(*coords, fill=color, width=3 if i == self.seleccionado else 1)
            x, y = punto(self.generacion, self.historia[self.generacion][i].x)
            c.create_oval(x - 3, y - 3, x + 3, y + 3, fill=color, outline="")
        x_actual, _ = punto(self.generacion, self.funcion.minimo)
        c.create_line(x_actual, arr, x_actual, aba, fill="#334155", dash=(4, 3))


def verificar() -> None:
    for funcion in FUNCIONES:
        print(f"{funcion.nombre}: f({funcion.optimo_x}) = {funcion.evaluar(funcion.optimo_x):.6f}")
        historia = ejecutar(funcion, Configuracion())
        mejor = max(historia[-1], key=lambda ind: ind.aptitud)
        print(f"  Mejor en generación 60: x={mejor.x:.6f}, f(x)={mejor.aptitud:.6f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualización del Proyecto 1")
    parser.add_argument("--verificar", action="store_true", help="Comprobar sin abrir la interfaz")
    args = parser.parse_args()
    if args.verificar:
        verificar()
    else:
        raiz = tk.Tk()
        Aplicacion(raiz)
        raiz.mainloop()
