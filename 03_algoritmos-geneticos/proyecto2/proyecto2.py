"""Resultados numéricos del Proyecto 2, sin gráficas."""
from __future__ import annotations

import argparse
import csv
from html import escape
from pathlib import Path
from algoritmo import Configuracion, crear_funcion, ejecutar, mejor


def mostrar_ventana(historia, funcion, cfg, html_path: Path) -> None:
    """Presenta los resultados en una tabla visual de Tkinter."""
    import tkinter as tk
    from tkinter import ttk
    import webbrowser

    raiz = tk.Tk()
    raiz.title("Proyecto 2 · Tabla de generaciones")
    raiz.geometry("1120x760")
    raiz.minsize(760, 520)
    raiz.configure(bg="#eef3f8")

    estilo = ttk.Style(raiz)
    if "clam" in estilo.theme_names():
        estilo.theme_use("clam")
    estilo.configure("Resultados.Treeview", background="white", foreground="#17283c",
                     fieldbackground="white", rowheight=30, font=("Sans", 10), borderwidth=0)
    estilo.configure("Resultados.Treeview.Heading", background="#173d58", foreground="white",
                     font=("Sans", 10, "bold"), padding=(10, 11), relief="flat")
    estilo.map("Resultados.Treeview", background=[("selected", "#d4edf3")],
               foreground=[("selected", "#12384c")])

    cont = tk.Frame(raiz, bg="#eef3f8", padx=20, pady=18)
    cont.pack(fill="both", expand=True)
    cabecera = tk.Frame(cont, bg="#155775", padx=25, pady=20)
    cabecera.pack(fill="x")
    tk.Label(cabecera, text="PROYECTO 2 · RESULTADOS NUMÉRICOS", bg="#155775",
             fg="#9ee4ee", font=("Sans", 9, "bold")).pack(anchor="w")
    tk.Label(cabecera, text="Tabla de generaciones", bg="#155775", fg="white",
             font=("Sans", 22, "bold")).pack(anchor="w", pady=(4, 3))
    tk.Label(cabecera, text=f"{funcion.nombre} · Objetivo: {funcion.objetivo}",
             bg="#155775", fg="#d9edf5", font=("Sans", 11)).pack(anchor="w")

    ganador = mejor(historia[-1], funcion)
    tarjetas = tk.Frame(cont, bg="#eef3f8")
    tarjetas.pack(fill="x", pady=(16, 12))
    datos = (
        ("MEJOR VALOR FINAL", f"{ganador.valor:.6f}"),
        ("MEJOR CROMOSOMA", ", ".join(f"x{i + 1}={x:.4f}" for i, x in enumerate(ganador.genes))),
        ("GENERACIONES", str(len(historia) - 1)),
    )
    for columna, (etiqueta, valor) in enumerate(datos):
        tarjeta = tk.Frame(tarjetas, bg="white", padx=16, pady=13,
                           highlightbackground="#dce5ef", highlightthickness=1)
        tarjeta.grid(row=0, column=columna, sticky="nsew", padx=(0, 10) if columna < 2 else 0)
        tarjetas.grid_columnconfigure(columna, weight=1)
        tk.Label(tarjeta, text=etiqueta, bg="white", fg="#64788d",
                 font=("Sans", 9, "bold")).pack(anchor="w")
        tk.Label(tarjeta, text=valor, bg="white", fg="#17283c", font=("Sans", 12, "bold"),
                 wraplength=380, justify="left").pack(anchor="w", pady=(7, 0))

    barra = tk.Frame(cont, bg="#eef3f8")
    barra.pack(fill="x", pady=(2, 10))
    tk.Label(barra, text="RESULTADOS DE CADA GENERACIÓN", bg="#eef3f8", fg="#17465c",
             font=("Sans", 11, "bold")).pack(side="left")
    tk.Button(barra, text="Abrir tabla HTML", bg="#136781", fg="white", activebackground="#0b526a",
              activeforeground="white", relief="flat", padx=14, pady=7, cursor="hand2",
              command=lambda: webbrowser.open(html_path.as_uri())).pack(side="right")

    marco = tk.Frame(cont, bg="white", highlightbackground="#dce5ef", highlightthickness=1)
    marco.pack(fill="both", expand=True)
    columnas = ("generacion", "mejor", "media", *(f"x{i + 1}" for i in range(len(funcion.limites))))
    tabla = ttk.Treeview(marco, columns=columnas, show="headings", style="Resultados.Treeview")
    nombres = ("Generación", "Mejor valor", "Media", *(f"x{i + 1}" for i in range(len(funcion.limites))))
    for clave, nombre in zip(columnas, nombres):
        tabla.heading(clave, text=nombre)
        tabla.column(clave, anchor="center", width=145 if clave != "generacion" else 110,
                    minwidth=90, stretch=True)
    tabla.tag_configure("par", background="#f5f9fc")
    tabla.tag_configure("ultimo", background="#e1f3ec")
    for numero, poblacion in enumerate(historia):
        individuo = mejor(poblacion, funcion)
        media = sum(ind.valor for ind in poblacion) / len(poblacion)
        valores = (numero, f"{individuo.valor:.6f}", f"{media:.6f}",
                   *(f"{x:.6f}" for x in individuo.genes))
        etiqueta = "ultimo" if numero == len(historia) - 1 else "par" if numero % 2 else ""
        tabla.insert("", "end", values=valores, tags=(etiqueta,))
    vertical = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
    horizontal = ttk.Scrollbar(marco, orient="horizontal", command=tabla.xview)
    tabla.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
    marco.grid_rowconfigure(0, weight=1)
    marco.grid_columnconfigure(0, weight=1)
    tabla.grid(row=0, column=0, sticky="nsew")
    vertical.grid(row=0, column=1, sticky="ns")
    horizontal.grid(row=1, column=0, sticky="ew")

    tk.Label(cont, text=f"Población: {cfg.poblacion}  ·  Cruce: {cfg.operador}  ·  Semilla: {cfg.semilla}  ·  Sin gráficas",
             bg="#eef3f8", fg="#587087", font=("Sans", 9)).pack(anchor="w", pady=(10, 0))
    raiz.mainloop()


def crear_tabla(historia, funcion, cfg, carpeta: Path) -> tuple[Path, Path]:
    """Guarda todas las generaciones como tabla HTML y CSV, sin gráficas."""
    columnas = [f"x{i + 1}" for i in range(len(funcion.limites))]
    filas = []
    for numero, poblacion in enumerate(historia):
        ganador = mejor(poblacion, funcion)
        media = sum(ind.valor for ind in poblacion) / len(poblacion)
        filas.append((numero, ganador.valor, media, *ganador.genes))

    csv_path = carpeta / "tabla_resultados.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["generacion", "mejor_valor", "media", *columnas])
        escritor.writerows(filas)

    ganador_final = mejor(historia[-1], funcion)
    cabeceras = "".join(f"<th scope='col'>{escape(col)}</th>" for col in ["Generación", "Mejor valor", "Media", *columnas])
    cuerpo = "\n".join(
        "<tr>" + "".join(f"<td>{valor:d}</td>" if indice == 0 else f"<td>{valor:.6f}</td>"
                            for indice, valor in enumerate(fila)) + "</tr>"
        for fila in filas
    )
    nombre = escape(funcion.nombre)
    referencia = escape(str(funcion.referencia))
    objetivo = escape(funcion.objetivo)
    genes = ", ".join(f"x{i + 1} = {valor:.6f}" for i, valor in enumerate(ganador_final.genes))
    html_path = carpeta / "tabla_resultados.html"
    html_path.write_text(f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Proyecto 2 · Tabla de resultados</title>
<style>
:root{{font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;color:#17283c;background:#eef3f8}}
*{{box-sizing:border-box}}body{{margin:0}}main{{max-width:1200px;margin:auto;padding:30px 22px 50px}}
header{{background:linear-gradient(120deg,#102743,#155775 72%,#187991);color:white;border-radius:24px;padding:34px 40px;box-shadow:0 18px 40px #1034522b}}
.eyebrow{{font-size:.76rem;letter-spacing:.15em;font-weight:800;text-transform:uppercase;color:#9ee4ee}}h1{{font-size:clamp(1.7rem,3vw,2.5rem);margin:10px 0}}header p{{color:#d9edf5;line-height:1.5;margin:0}}
.cards{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:15px;margin:18px 0}}.card,.panel{{background:white;border:1px solid #dce5ef;border-radius:18px;padding:20px;box-shadow:0 8px 26px #18324a0b}}
.label{{display:block;font-size:.75rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:#64788d;margin-bottom:9px}}.value{{display:block;font-size:1.25rem;font-weight:800;overflow-wrap:anywhere}}.small{{color:#587087;line-height:1.5}}.panel h2{{margin:0 0 6px;font-size:1.15rem}}.meta{{display:flex;gap:10px;flex-wrap:wrap;margin:15px 0 20px}}.meta span{{background:#ecf7f8;color:#17647a;padding:7px 11px;border-radius:999px;font-size:.84rem;font-weight:700}}
.table-wrap{{overflow:auto;max-height:630px;border:1px solid #dce5ef;border-radius:12px}}table{{border-collapse:collapse;width:100%;min-width:630px;font-variant-numeric:tabular-nums}}th,td{{padding:11px 14px;text-align:right;border-bottom:1px solid #e6edf3;white-space:nowrap}}th:first-child,td:first-child{{text-align:left}}thead th{{position:sticky;top:0;background:#173d58;color:white;font-size:.82rem;z-index:1}}tbody tr:nth-child(even){{background:#f5f9fc}}tbody tr:hover{{background:#e7f5f8}}tbody tr:last-child{{background:#e1f3ec;font-weight:800}}footer{{text-align:center;color:#6d8295;font-size:.82rem;margin-top:22px}}
@media(max-width:700px){{main{{padding:12px 12px 30px}}header{{padding:26px 22px}}.cards{{grid-template-columns:1fr}}.panel{{padding:16px}}}}
</style></head><body><main>
<header><div class="eyebrow">Proyecto 2 · Resultados numéricos</div><h1>Tabla de generaciones</h1><p>{nombre} · Objetivo: {objetivo}. Consulta el mejor valor, la media y las variables de cada generación.</p></header>
<div class="cards"><div class="card"><span class="label">Mejor valor final</span><span class="value">{ganador_final.valor:.6f}</span></div><div class="card"><span class="label">Mejor cromosoma</span><span class="value">{genes}</span></div><div class="card"><span class="label">Generaciones registradas</span><span class="value">{len(filas)}</span></div></div>
<section class="panel"><h2>Resultados de la ejecución</h2><p class="small">Referencia del libro: {referencia}</p><div class="meta"><span>Población: {cfg.poblacion}</span><span>Variables: {len(columnas)}</span><span>Cruce: {escape(cfg.operador)}</span><span>Mutación: {cfg.mutacion:g}</span><span>Semilla: {cfg.semilla}</span></div>
<div class="table-wrap"><table><thead><tr>{cabeceras}</tr></thead><tbody>{cuerpo}</tbody></table></div></section>
<footer>Generado con Python · Sin bibliotecas externas</footer></main></body></html>""", encoding="utf-8")
    return html_path, csv_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Proyecto 2: optimización genética con genes reales")
    parser.add_argument("--funcion", choices=("max1", "max2", "min1", "rastrigin", "schwefel"), default="schwefel")
    parser.add_argument("--n", type=int, default=3, help="Variables en Rastrigin o Schwefel (1-20)")
    parser.add_argument("--poblacion", type=int, default=60)
    parser.add_argument("--generaciones", type=int, default=150)
    parser.add_argument("--cruce", type=float, default=0.8, help="Probabilidad de cruce (0-1)")
    parser.add_argument("--mutacion", type=float, default=0.03, help="Probabilidad de mutación por gen (0-1)")
    parser.add_argument("--operador", choices=("sbx", "aritmetico", "uniforme", "un_punto"), default="sbx")
    parser.add_argument("--semilla", type=int, default=8)
    parser.add_argument("--sin-elitismo", action="store_true")
    parser.add_argument("--cada", type=int, default=10, help="Mostrar una fila cada N generaciones")
    parser.add_argument("--consola", action="store_true", help="No abrir la ventana visual; solo mostrar y guardar la tabla")
    args = parser.parse_args()
    if args.cada < 1:
        parser.error("--cada debe ser mayor que cero")
    try:
        funcion = crear_funcion(args.funcion, args.n)
        cfg = Configuracion(args.poblacion, args.generaciones, args.cruce,
                            args.mutacion, not args.sin_elitismo, args.semilla,
                            args.operador)
        historia = ejecutar(funcion, cfg)
    except ValueError as exc:
        parser.error(str(exc))

    print(f"{funcion.nombre} | objetivo: {funcion.objetivo}")
    print(f"Referencia del libro: {funcion.referencia}")
    print(f"Genes reales: {len(funcion.limites)} | cruce: {cfg.operador} | población: {cfg.poblacion}")
    print("Generación        Mejor valor       Media")
    for numero, poblacion in enumerate(historia):
        if numero % args.cada == 0 or numero == len(historia) - 1:
            valor = mejor(poblacion, funcion).valor
            media = sum(ind.valor for ind in poblacion) / len(poblacion)
            print(f"{numero:10d}  {valor:17.6f}  {media:12.6f}")
    ganador = mejor(historia[-1], funcion)
    print("Mejor cromosoma:", ", ".join(f"x{i+1}={x:.6f}" for i, x in enumerate(ganador.genes)))
    print(f"Valor de la función: {ganador.valor:.6f}")
    html_path, csv_path = crear_tabla(historia, funcion, cfg, Path(__file__).parent)
    print(f"Tabla completa: {html_path}")
    print(f"Datos CSV: {csv_path}")
    if not args.consola:
        try:
            mostrar_ventana(historia, funcion, cfg, html_path)
        except ImportError as exc:
            print(f"No se pudo abrir Tkinter: {exc}. Abre la tabla HTML.")
        except Exception as exc:
            # En servidores sin pantalla, la tabla HTML sigue disponible.
            if exc.__class__.__name__ == "TclError":
                print("No hay pantalla disponible. Abre la tabla HTML en un equipo con escritorio.")
            else:
                raise


if __name__ == "__main__":
    main()
