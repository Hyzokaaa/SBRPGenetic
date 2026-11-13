"""
Informe de resultados de uno o varios lanzamientos de app/main.py (o app/grid.py): calidad respecto al mejor valor
conocido, comparación con los trabajos anteriores y entre configuraciones, por tipo de instancia, con gráficas.

Genera report.md, report.html (autocontenido), report.pdf (si hay Edge, Chrome o Chromium) y las tablas en CSV.

Ejemplos (desde la raíz del proyecto):
    python app/report.py results/20261113_173406
    python app/report.py results/20261113_150004 results/20261113_173406
"""
import argparse
import base64
import datetime as dt
import html
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402

from src.analysis import report  # noqa: E402

# Colores categóricos en orden fijo (los mismos que la interfaz) y tinta de textos y ejes
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e6e4dd"
BROWSERS = ["msedge", "chrome", "chromium", "chromium-browser", "google-chrome",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"]


# ------------------------- Formato -------------------------
def percent(value, sign=True):
    return "—" if value != value else (f"{value:+.2%}" if sign else f"{value:.0%}")


def p_value(value):
    return "—" if value != value else ("< 0.001" if value < 0.001 else f"{value:.3f}")


def formatted(frame, formats: dict, columns: dict):
    """Tabla con columnas renombradas y valores formateados como texto."""
    frame = frame.copy()
    for column, function in formats.items():
        if column in frame:
            frame[column] = frame[column].map(function)
    return frame[list(columns)].rename(columns=columns).astype(str)


# ------------------------- Gráficas -------------------------
def style(ax, title, ylabel):
    ax.set_title(title, loc="left", fontsize=11, color=INK, pad=10)
    ax.set_ylabel(ylabel, color=MUTED, fontsize=9)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)


def grouped_bars(path, groups, series: dict, title, ylabel, percent_axis=True):
    """Barras agrupadas: una serie por elemento de series ({nombre: [valor por grupo]}), colores en orden fijo."""
    fig, ax = plt.subplots(figsize=(8, 3.6), dpi=150)
    width = 0.8 / max(1, len(series))
    for index, (name, values) in enumerate(series.items()):
        positions = [g + (index - (len(series) - 1) / 2) * width for g in range(len(groups))]
        bars = ax.bar(positions, values, width * 0.92, label=name, color=SERIES[index % len(SERIES)])
        if len(series) <= 3:
            ax.bar_label(bars, labels=[percent(v) if percent_axis else f"{v:.1f}" for v in values], fontsize=7,
                         color=MUTED, padding=2)
    ax.set_xticks(range(len(groups)), [str(g) for g in groups])
    if percent_axis:
        ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.axhline(0, color=MUTED, linewidth=0.8)
    style(ax, title, ylabel)
    if len(series) > 1:
        ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def sorted_gaps(path, table):
    """Gap de cada instancia ordenado de menor a mayor, una línea por configuración."""
    fig, ax = plt.subplots(figsize=(8, 3.6), dpi=150)
    for index, (label, data) in enumerate(table.groupby("etiqueta", sort=False)):
        values = sorted(data["gap_mejor"].dropna())
        ax.plot(range(1, len(values) + 1), values, color=SERIES[index % len(SERIES)], linewidth=2, label=label)
    ax.axhline(0, color=MUTED, linewidth=0.8)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_xlabel("Instancias ordenadas por gap", color=MUTED, fontsize=9)
    style(ax, "Gap de cada instancia sobre el mejor valor conocido (mejor de las semillas)", "Gap")
    if table["etiqueta"].nunique() > 1:
        ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


# ------------------------- Contenido -------------------------
def build(folders, output: Path):
    runs = report.load_runs(folders)
    table = report.per_instance(runs)
    labels = list(dict.fromkeys(table["etiqueta"]))
    quality = report.quality(table)
    references = report.against_references(table)
    new_best = report.new_best_known(table)
    groups = {key: report.by_group(table, key) for key in report.GROUPS}
    worst = report.worst(table)
    pairs = report.between_configs(table) if len(labels) > 1 else None

    # Tablas en CSV (valores sin formato)
    table.to_csv(output / "por_instancia.csv", index=False)
    quality.to_csv(output / "calidad.csv", index=False)
    references.to_csv(output / "antecedentes.csv", index=False)
    new_best.to_csv(output / "nuevos_mejores.csv", index=False)
    for key, frame in groups.items():
        frame.to_csv(output / f"por_{key}.csv", index=False)
    if pairs is not None:
        pairs.to_csv(output / "entre_configuraciones.csv", index=False)

    # Gráficas
    w_values = sorted(table["w"].dropna().unique())
    by_w = groups["w"]
    grouped_bars(output / "gap_por_w.png", w_values,
                 {label: [by_w[(by_w["configuración"] == label) & (by_w[report.GROUPS["w"]] == w)]["gap_medio_mejor"]
                          .mean() for w in w_values] for label in labels},
                 "Gap medio sobre el mejor valor conocido según la distancia a pie", "Gap medio")
    figures = [("gap_por_w.png", "Gap medio sobre el mejor valor conocido según la distancia máxima a pie (w).")]
    for index, label in enumerate(labels[:3]):
        data = by_w[by_w["configuración"] == label]
        name = f"antecedentes_por_w_{index + 1}.png"
        grouped_bars(output / name, w_values,
                     {"Frente a Schittekat (2013)": list(data["vs_schittekat"]),
                      "Frente a la tesis (2020)": list(data["vs_tesis"])},
                     f"{label}: diferencia media frente a los antecedentes (negativo = mejor)", "Diferencia media")
        figures.append((name, f"{label}: diferencia media con Schittekat y con la tesis de Pérez Pérez por distancia "
                              "a pie. Por debajo de cero, nuestras soluciones son más cortas."))
    sorted_gaps(output / "gaps_ordenados.png", table)
    figures.append(("gaps_ordenados.png", "Gap de cada instancia, de menor a mayor: muestra cuántas instancias están "
                                          "en el mejor valor conocido y cuán lejos quedan las demás."))

    best_of_seeds = references[references["valor"] == "mejor de las semillas"]
    cards = []
    for _, row in quality.iterrows():
        mine = best_of_seeds[best_of_seeds["configuración"] == row["configuración"]].set_index("referencia")
        versus = lambda column: mine["diferencia_media"].get(report.REFERENCES[column], float("nan"))
        cards.append((row["configuración"], [
            ("Gap medio", percent(row["gap_medio_mejor"]), "sobre el mejor valor conocido"),
            ("Gap mediano", percent(row["gap_mediano_mejor"]), "la mitad de las instancias, por debajo"),
            ("Igualan / mejoran", f"{row['igualan_mejor_conocido']} / {row['nuevos_mejores']}",
             f"el mejor conocido, de {row['instancias']} instancias"),
            ("Óptimos alcanzados", f"{row['óptimos_alcanzados']} / {row['óptimos_probados']}", "óptimos probados"),
            ("Frente a Schittekat", percent(versus("grasp_vnd")), "diferencia media (negativo = mejor)"),
            ("Frente a la tesis", percent(versus("hill_climbing_2020")), "diferencia media (negativo = mejor)")]))

    sections = []
    sections.append(("Resumen", [
        f"Lanzamientos: {', '.join(Path(f).name for f in folders)}. Configuraciones: {', '.join(labels)}.",
        "El gap es la diferencia relativa con el mejor valor conocido de cada instancia (0 % = lo iguala; negativo = "
        "lo mejora). «Mejor» es el mejor resultado de las semillas de cada instancia y «media», la media de las "
        "semillas."], [formatted(quality, {
            "factibles": lambda v: percent(v, sign=False), "gap_medio_mejor": percent, "gap_mediano_mejor": percent,
            "gap_medio_media": percent, "tiempo_medio": lambda v: f"{v:.1f} s"}, {
            "configuración": "Configuración", "instancias": "Instancias", "corridas": "Corridas", "factibles": "Factibles",
            "gap_medio_mejor": "Gap medio (mejor)", "gap_medio_media": "Gap medio (media)",
            "tiempo_medio": "Tiempo medio por corrida"})], [figures[0]]))
    sections.append(("Comparación con los trabajos anteriores", [
        "Instancias en que cada configuración obtiene una solución más corta (mejor), igual (diferencia menor que "
        f"{report.TIE:.2%}) o más larga (peor) que cada trabajo anterior, diferencia relativa media (negativa = "
        "mejor) y p-valor de la prueba de rangos con signo de Wilcoxon (bilateral): por debajo de 0.05 la diferencia "
        "es estadísticamente significativa. Se compara el mejor resultado de las semillas de cada instancia; la "
        "comparación con la media de las semillas está en antecedentes.csv."], [formatted(best_of_seeds, {
            "diferencia_media": percent, "p_wilcoxon": p_value}, {
            "configuración": "Configuración", "referencia": "Referencia", "instancias": "Instancias",
            "mejor": "Mejor", "igual": "Igual", "peor": "Peor", "diferencia_media": "Diferencia media",
            "p_wilcoxon": "p (Wilcoxon)"})], figures[1:-1]))
    sections.append(("Por tipo de instancia", [
        "Gap medio sobre el mejor valor conocido y diferencia media con Schittekat y con la tesis por grupo de "
        "instancias."], [formatted(frame, {
            "gap_medio_mejor": percent, "vs_schittekat": percent, "vs_tesis": percent,
            "tiempo_medio": lambda v: f"{v:.1f} s"}, {
            "configuración": "Configuración", report.GROUPS[key]: report.GROUPS[key], "instancias": "Instancias",
            "gap_medio_mejor": "Gap medio (mejor)", "vs_schittekat": "Frente a Schittekat", "vs_tesis": "Frente a la tesis",
            "tiempo_medio": "Tiempo medio"}) for key, frame in groups.items()], [figures[-1]]))
    sections.append(("Nuevos mejores valores conocidos", [
        "Instancias en que se mejora el mejor valor conocido. Se comprueba que el valor no quede por debajo de la "
        "cota inferior publicada (si existe), lo que indicaría un error." if len(new_best) else
        "Ninguna configuración mejora el mejor valor conocido de alguna instancia."],
        [formatted(new_best, {"mejor": lambda v: f"{v:.2f}", "best_known": lambda v: f"{v:.2f}",
                              "gap_mejor": percent, "lower_bound": lambda v: "—" if v != v else f"{v:.2f}",
                              "respeta_cota": lambda v: "sí" if v else "NO"}, {
            "etiqueta": "Configuración", "instance": "Instancia", "mejor": "Nuestro valor",
            "best_known": "Mejor conocido", "gap_mejor": "Mejora", "lower_bound": "Cota inferior",
            "respeta_cota": "Respeta la cota"})] if len(new_best) else [], []))
    sections.append(("Instancias con mayor gap", ["Las 10 instancias más lejos del mejor valor conocido de cada "
                                                   "configuración."], [formatted(worst, {
        "mejor": lambda v: f"{v:.2f}", "best_known": lambda v: f"{v:.2f}", "gap_mejor": percent,
        "optimal": lambda v: "sí" if v is True else "no"}, {
        "etiqueta": "Configuración", "instance": "Instancia", "mejor": "Nuestro valor", "best_known": "Mejor conocido",
        "gap_mejor": "Gap", "optimal": "Óptimo probado", "w": "w"})], []))
    if pairs is not None:
        sections.append(("Comparación entre configuraciones", [
            "Instancias comunes en que la primera configuración es mejor, igual o peor que la segunda (mejor de las "
            "semillas), diferencia relativa media y prueba de Wilcoxon."], [formatted(pairs, {
                "diferencia_media": percent, "p_wilcoxon": p_value}, {
                "configuración": "Configuración", "frente_a": "Frente a", "instancias": "Instancias", "mejor": "Mejor",
                "igual": "Igual", "peor": "Peor", "diferencia_media": "Diferencia media", "p_wilcoxon": "p (Wilcoxon)"})],
            []))
    sections.append(("Referencias", [
        "Schittekat, P., Kinable, J., Sörensen, K., Sevaux, M., Spieksma, F. y Springael, J. (2013). A metaheuristic "
        "for the school bus routing problem with bus stop selection. European Journal of Operational Research, "
        "229(2), 518–528.",
        "Pérez Pérez, A. C. (2020). Una solución para el problema de planificación de rutas de autobuses escolares "
        "(tesis). CUJAE, La Habana.",
        "Pérez-Rodríguez, R. y Hernández-Aguirre, A. (2016): resultados del EDA tomados de la tesis anterior. En 12 "
        "instancias quedan por debajo de óptimos probados, por lo que no se usan como mejor valor conocido."], [], []))
    return sections, cards


# ------------------------- Salidas -------------------------
def markdown_table(frame) -> str:
    header = "| " + " | ".join(frame.columns) + " |"
    rule = "|" + "|".join("---" for _ in frame.columns) + "|"
    rows = ["| " + " | ".join(str(v).replace("|", "\\|") for v in row) + " |" for row in frame.itertuples(index=False)]
    return "\n".join([header, rule, *rows])


def write_markdown(path: Path, title, sections, cards):
    lines = [f"# {title}", ""]
    for name, items in cards:
        lines += [f"**{name}**: " + " · ".join(f"{label} {value}" for label, value, _ in items), ""]
    for number, (heading, paragraphs, tables, figures) in enumerate(sections, 1):
        lines += [f"## {number}. {heading}", ""]
        for paragraph in paragraphs:
            lines += [paragraph, ""]
        for table in tables:
            lines += [markdown_table(table), ""]
        for name, caption in figures:
            lines += [f"![{caption}]({name})", "", f"*{caption}*", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


CSS = """
:root { --ink: #1d1d1b; --muted: #5f5e5a; --rule: #e4e2da; --surface: #ffffff; --head: #2a78d6; --zebra: #f7f6f2;
        --card: #f4f7fc; --accent: #2a78d6; }
@page { size: A4; margin: 16mm 14mm; }
body { background: var(--surface); color: var(--ink); font: 13px/1.55 "Segoe UI", system-ui, -apple-system, sans-serif;
       max-width: 1080px; margin: 0 auto; padding: 32px 16px 48px; }
header { border-bottom: 3px solid var(--accent); padding-bottom: 12px; margin-bottom: 20px; }
h1 { font-size: 22px; margin: 0 0 4px; letter-spacing: -0.01em; }
.meta { color: var(--muted); font-size: 12px; margin: 0; }
h2 { font-size: 16px; margin: 28px 0 8px; color: var(--accent); }
h2 span { color: var(--muted); font-weight: 400; margin-right: 6px; }
p { color: var(--muted); margin: 6px 0 10px; }
.config { font-weight: 600; margin: 14px 0 6px; }
.cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 8px; }
.card { background: var(--card); border-radius: 8px; padding: 10px 12px; break-inside: avoid; }
.card .label { color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; }
.card .value { font-size: 22px; font-weight: 600; font-variant-numeric: tabular-nums; margin: 2px 0; }
.card .note { color: var(--muted); font-size: 11px; }
table { border-collapse: collapse; width: 100%; margin: 8px 0 18px; font-size: 11.5px;
        font-variant-numeric: tabular-nums; break-inside: auto; }
thead { display: table-header-group; }
th { background: var(--head); color: #fff; font-weight: 600; text-align: left; padding: 6px 8px; }
td { padding: 5px 8px; border-bottom: 1px solid var(--rule); }
tbody tr:nth-child(even) td { background: var(--zebra); }
td.num, th.num { text-align: right; white-space: nowrap; }
tr { break-inside: avoid; }
figure { margin: 10px 0 22px; break-inside: avoid; } img { max-width: 100%; display: block; }
figcaption { color: var(--muted); font-size: 11.5px; margin-top: 4px; }
.scroll { overflow-x: auto; }
@media print { body { max-width: none; padding: 0; } h2 { break-after: avoid; } .scroll { overflow: visible; } }
@media (max-width: 700px) { .cards { grid-template-columns: repeat(2, 1fr); } }
"""


def is_number(text: str) -> bool:
    cleaned = text.replace("%", "").replace("+", "").replace("−", "").replace("<", "").replace("s", "").replace("/", "")
    cleaned = cleaned.replace(" ", "").replace(".", "").replace("-", "").replace("—", "")
    return cleaned.isdigit() or text.strip() == "—"


def html_table(frame) -> str:
    """Tabla HTML con las columnas numéricas alineadas a la derecha."""
    numeric = [all(is_number(str(value)) for value in frame[column]) for column in frame.columns]
    head = "".join(f"<th class='{'num' if n else ''}'>{html.escape(str(c))}</th>" for c, n in zip(frame.columns, numeric))
    rows = "".join("<tr>" + "".join(f"<td class='{'num' if n else ''}'>{html.escape(str(v))}</td>"
                                    for v, n in zip(row, numeric)) + "</tr>" for row in frame.itertuples(index=False))
    return f"<div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>"


def write_html(path: Path, title, sections, cards, output: Path):
    parts = [f"<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' "
             f"content='width=device-width, initial-scale=1'><title>{html.escape(title)}</title><style>{CSS}</style>"
             f"</head><body><header><h1>{html.escape(title)}</h1><p class='meta'>Generado el "
             f"{dt.datetime.now():%d/%m/%Y %H:%M} con app/report.py</p></header>"]
    for name, items in cards:
        parts.append(f"<div class='config'>{html.escape(name)}</div><div class='cards'>")
        parts += [f"<div class='card'><div class='label'>{html.escape(label)}</div><div class='value'>"
                  f"{html.escape(value)}</div><div class='note'>{html.escape(note)}</div></div>"
                  for label, value, note in items]
        parts.append("</div>")
    for number, (heading, paragraphs, tables, figures) in enumerate(sections, 1):
        parts.append(f"<h2><span>{number}.</span>{html.escape(heading)}</h2>")
        parts += [f"<p>{html.escape(paragraph)}</p>" for paragraph in paragraphs]
        parts += [html_table(table) for table in tables]
        for name, caption in figures:
            data = base64.b64encode((output / name).read_bytes()).decode()
            parts.append(f"<figure><img src='data:image/png;base64,{data}' alt='{html.escape(caption)}'>"
                         f"<figcaption>{html.escape(caption)}</figcaption></figure>")
    parts.append("</body></html>")
    path.write_text("".join(parts), encoding="utf-8")


def find_browser():
    candidate = os.environ.get("SBRP_BROWSER")
    for name in ([candidate] if candidate else []) + BROWSERS:
        found = shutil.which(name) or (name if Path(name).is_file() else None)
        if found:
            return found
    return None


def write_pdf(html_path: Path, pdf_path: Path) -> bool:
    """Convierte el HTML en PDF con un navegador sin ventana (Edge, Chrome o Chromium)."""
    browser = find_browser()
    if browser is None:
        return False
    # Rutas absolutas: el navegador no usa el directorio de trabajo actual
    pdf_path = pdf_path.resolve()
    command = [browser, "--headless", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf_path}",
               html_path.resolve().as_uri()]
    try:
        subprocess.run(command, capture_output=True, timeout=180)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return pdf_path.exists() and pdf_path.stat().st_size > 0


def main():
    args = parse_args()
    folders = [Path(folder) if Path(folder).is_absolute() else ROOT / folder for folder in args.launches]
    missing = [str(folder) for folder in folders if not (folder / "summary.csv").exists()]
    if missing:
        sys.exit(f"Sin summary.csv (¿lanzamiento sin terminar?): {', '.join(missing)}")
    if args.output:
        output = Path(args.output).resolve()
    elif len(folders) == 1:
        output = folders[0] / "report"
    else:
        output = ROOT / "results" / f"report_{dt.datetime.now():%Y%m%d_%H%M%S}"
    output.mkdir(parents=True, exist_ok=True)

    sections, cards = build(folders, output)
    title = args.title or "Informe de resultados del algoritmo genético para el SBRP"
    write_markdown(output / "report.md", title, sections, cards)
    write_html(output / "report.html", title, sections, cards, output)
    pdf = write_pdf(output / "report.html", output / "report.pdf") if not args.no_pdf else False
    print(f"Informe en {output}: report.md, report.html{', report.pdf' if pdf else ''}, tablas CSV y gráficas PNG")
    if not pdf and not args.no_pdf:
        print("No se generó el PDF: no se encontró Edge, Chrome ni Chromium (indica la ruta con SBRP_BROWSER).")


def parse_args():
    parser = argparse.ArgumentParser(description="Informe de resultados de uno o varios lanzamientos.")
    parser.add_argument("launches", nargs="+", help="Carpetas de lanzamiento (results/<fecha_hora>) con summary.csv")
    parser.add_argument("--output", help="Carpeta del informe (por defecto <lanzamiento>/report o results/report_<fecha>)")
    parser.add_argument("--title", help="Título del informe")
    parser.add_argument("--no-pdf", action="store_true", help="No generar el PDF")
    return parser.parse_args()


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    main()
