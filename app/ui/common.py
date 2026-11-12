"""
Utilidades compartidas por las páginas de la interfaz: rutas del proyecto, carga de instancias y configuraciones,
instanciación de operadores y figuras de Plotly.
"""
import importlib
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.graph_objects as go

from src.algorithm.genetic_algorithm.genetic_algorithm_config import GeneticAlgorithmConfig
from src.operators.distance.distance_euclidean import EuclideanDistance
from src.problems.problem_sbrp.algorithm.genetic_algorithm.operators_enum import Operators
from src.problems.problem_sbrp.data_io.file_data_input_sbrp import FileDataInputSBRP
from src.problems.problem_sbrp.model.school import School
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP

logging.disable(logging.INFO)

INSTANCES_DIR = ROOT / "data" / "instances"
CONFIGS_DIR = ROOT / "src" / "problems" / "problem_sbrp" / "algorithm" / "genetic_algorithm"
RESULTS_DIR = ROOT / "results"

# Paleta (referencia de la guía de visualización): categórica en orden fijo, secuencial azul y neutros
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]
# Paleta categórica completa en orden fijo (máximo 8 series; nunca se repiten colores)
SERIES_ALL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
NEUTRAL = "#9a9890"
TEXT_MUTED = "#52514e"
# Rampas de ocupación (de menos a más llena), todas con contraste >= 3:1 sobre su fondo (WCAG 1.4.11):
# en tema claro, más llena = más oscura; en tema oscuro, más llena = más clara.
SEQUENTIAL = ["#3987e5", "#256abf", "#104281"]
SEQUENTIAL_DARK = ["#256abf", "#5598e7", "#9ec5f4"]
# Fondo para resaltar celdas de tablas (siempre con texto oscuro)
TABLE_HIGHLIGHT = "#cde2fb"
HIGHLIGHT = "#eb6834"
# Tinta de los puntos fijos del mapa (escuela y paradas) y color de su contorno, según el tema claro u oscuro
INK = {False: ("#0b0b0b", TEXT_MUTED, "white"), True: ("#f4f3ef", "#c9c7bf", "#0e1117")}

EDGE_COLORS = {"A": SERIES[0], "B": SERIES[1], "nueva": SERIES[2], "AB": NEUTRAL}
# El origen de una arista se codifica también con el trazo, para no depender solo del color
EDGE_DASH = {"A": "solid", "B": "dash", "nueva": "dot", "AB": "solid"}
EDGE_LABELS = {"A": "Del padre A", "B": "Del padre B", "nueva": "Nueva", "AB": "Común a ambos padres"}

STOP_REASONS = {"stagnation": "estancamiento", "max_iter": "límite de generaciones"}

INSTANCE_HELP = ("El nombre codifica la instancia: inst<N>-<k>s<paradas>-<estudiantes>-c<capacidad>-w<distancia a pie>. "
                 "La instancia elegida se mantiene al cambiar de página.")


# ------------------------- Instancias, configuraciones y operadores -------------------------
def list_instances():
    """{etiqueta: ruta} de todas las instancias, agrupadas por carpeta."""
    instances = {}
    for folder in sorted(p for p in INSTANCES_DIR.iterdir() if p.is_dir()):
        for file in sorted(folder.glob("*.xpress"), key=lambda f: _natural_key(f.name)):
            instances[f"{folder.name}/{file.name}"] = file
    return instances


def instance_name(label: str) -> str:
    """Etiqueta de una instancia sin la extensión del archivo."""
    return label.removesuffix(".xpress")


def list_configs():
    """{nombre: ruta} de las configuraciones config<N>.json, ordenadas por número."""
    files = sorted(CONFIGS_DIR.glob("config*.json"), key=lambda f: _natural_key(f.name))
    return {f.stem: f for f in files}


def read_config(path) -> dict:
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def operator_names(family: str):
    """Nombres del enumerado de operadores por familia."""
    names = [op.name for op in Operators]
    families = {
        "crossover": [n for n in names if "CROSSOVER" in n],
        "mutation": [n for n in names if "MUTATION" in n],
        "selection": [n for n in names if "SELECTION" in n],
        "route_generator": [n for n in names if "ROUTE_GENERAT" in n],
        "stop_assign": [n for n in names if n.endswith("_STRATEGY") and "STUDENT" in n],
    }
    return families[family]


def instantiate(name: str, **params):
    module_name, class_name = Operators[name].value.rsplit('.', 1)
    return getattr(importlib.import_module(module_name), class_name)(**params)


def operator_label(name: str) -> str:
    return name.replace("_OPERATOR", "").replace("_SBRP", "").replace("_STRATEGY", "").replace("_", " ").title()


def build_config(config_path, instance_path, overrides: dict) -> GeneticAlgorithmConfig:
    """
    Carga una configuración y aplica los cambios indicados. Los valores de claves de operadores
    (que terminan en _operator o _strategy) son nombres del enumerado y se instancian.
    """
    config = GeneticAlgorithmConfig()
    config.load_from_file(str(config_path), str(instance_path))
    for key, value in overrides.items():
        if value is None:
            continue
        if key.endswith("_operator") or key.endswith("_strategy"):
            value = instantiate(value)
        setattr(config, key, value)
    return config


def load_problem(instance_path, assign_strategy: str = "H_STUDENT_TO_CLOSEST_STOP_STRATEGY") -> ProblemSBRP:
    """Construye el problema de una instancia y asigna los estudiantes a paradas."""
    problem = ProblemSBRP()
    problem.construct(FileDataInputSBRP(str(instance_path)).conform())
    instantiate(assign_strategy).generate_stop_assign(problem, EuclideanDistance())
    return problem


def _natural_key(text: str):
    import re
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", text)]


# ------------------------- Tablas -------------------------
def instance_summary(problem: ProblemSBRP) -> dict:
    used = [s for s in problem.stops if s.num_assigned_students > 0]
    total = sum(s.num_assigned_students for s in used)
    return {
        "Paradas (m)": len(problem.stops),
        "Paradas usadas": len(used),
        "Estudiantes (n)": len(problem.students),
        "Buses (v)": len(problem.vehicles),
        "Capacidad (c)": problem.bus_capacity,
        "Distancia a pie (w)": problem.w_distance,
        "Buses mínimos (⌈n/c⌉)": -(-total // problem.bus_capacity),
    }


SUMMARY_HELP = {
    "Paradas (m)": "Paradas candidatas de la instancia.",
    "Paradas usadas": "Paradas con al menos un estudiante asignado: son las que las rutas deben visitar.",
    "Estudiantes (n)": "Estudiantes que hay que recoger.",
    "Buses (v)": "Buses disponibles: número máximo de rutas.",
    "Capacidad (c)": "Estudiantes que caben en un bus.",
    "Distancia a pie (w)": "Distancia máxima que un estudiante puede caminar hasta su parada, en las unidades de las coordenadas.",
    "Buses mínimos (⌈n/c⌉)": "Cota inferior del número de rutas: estudiantes asignados entre la capacidad, redondeado hacia arriba.",
}


def route_stops(route):
    return [stop for stop in route.stops if stop is not None and not isinstance(stop, School)]


def routes_table(problem: ProblemSBRP, solution) -> pd.DataFrame:
    rows = []
    for i, route in enumerate(solution.get_representation(), 1):
        stops = route_stops(route)
        load = sum(s.num_assigned_students for s in stops)
        path = [problem.school] + stops + [problem.school]
        distance = sum(problem.distance_matrix[path[k].id][path[k + 1].id] for k in range(len(path) - 1))
        rows.append({"Ruta": i, "Paradas": " → ".join(str(s.id) for s in stops), "Nº paradas": len(stops),
                     "Estudiantes": load, "Ocupación": load / problem.bus_capacity, "Distancia": round(distance, 2)})
    return pd.DataFrame(rows)


# ------------------------- Figuras -------------------------
def _base_layout(fig: go.Figure, title: str = None, height: int = 520):
    fig.update_layout(
        title=title, height=height, margin=dict(l=10, r=10, t=40 if title else 10, b=10),
        hovermode="closest", legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x", scaleratio=1),
    )
    return fig


def _points_traces(problem: ProblemSBRP, show_students: bool, show_assignment: bool, dark: bool = False):
    school_color, stop_color, outline = INK[dark]
    traces = []
    if show_students:
        if show_assignment:
            xs, ys = [], []
            for st in problem.students:
                if st.assigned_stop is not None:
                    xs += [st.coordinates[0], st.assigned_stop.coordinates[0], None]
                    ys += [st.coordinates[1], st.assigned_stop.coordinates[1], None]
            traces.append(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=NEUTRAL, width=0.6),
                                     hoverinfo="skip", showlegend=False))
        traces.append(go.Scatter(
            x=[s.coordinates[0] for s in problem.students], y=[s.coordinates[1] for s in problem.students],
            mode="markers", name="Estudiante", marker=dict(size=4, color=NEUTRAL),
            text=[f"Estudiante {s.id}<br>Parada {s.assigned_stop.id if s.assigned_stop else '—'}" for s in problem.students],
            hovertemplate="%{text}<extra></extra>"))
    used = [s for s in problem.stops if s.num_assigned_students > 0]
    unused = [s for s in problem.stops if s.num_assigned_students == 0]
    if unused:
        traces.append(go.Scatter(
            x=[s.coordinates[0] for s in unused], y=[s.coordinates[1] for s in unused], mode="markers",
            name="Parada sin estudiantes", marker=dict(size=7, color="rgba(0,0,0,0)", line=dict(color=NEUTRAL, width=1)),
            text=[f"Parada {s.id} (sin estudiantes)" for s in unused], hovertemplate="%{text}<extra></extra>"))
    traces.append(go.Scatter(
        x=[s.coordinates[0] for s in used], y=[s.coordinates[1] for s in used], mode="markers",
        name="Parada (tamaño = estudiantes)",
        marker=dict(size=[8 + 10 * s.num_assigned_students / problem.bus_capacity for s in used],
                    color=stop_color, line=dict(color=outline, width=2)),
        text=[f"Parada {s.id}<br>{s.num_assigned_students} estudiantes" for s in used],
        hovertemplate="%{text}<extra></extra>"))
    traces.append(go.Scatter(
        x=[problem.school.coordinates[0]], y=[problem.school.coordinates[1]], mode="markers", name="Escuela",
        marker=dict(size=18, symbol="star", color=school_color, line=dict(color=outline, width=2)),
        hovertemplate="Escuela<extra></extra>"))
    return traces


def instance_figure(problem: ProblemSBRP, show_students=True, show_assignment=True, height=520,
                    dark: bool = False) -> go.Figure:
    fig = go.Figure(_points_traces(problem, show_students, show_assignment, dark))
    return _base_layout(fig, height=height)


# Umbral inferior de ocupación de cada tono de la rampa
OCCUPANCY_STEPS = [0.0, 0.5, 0.8]


def _ramp(dark: bool = False):
    return SEQUENTIAL_DARK if dark else SEQUENTIAL


def _load_color(occupancy: float, dark: bool = False) -> str:
    return _ramp(dark)[sum(occupancy >= step for step in OCCUPANCY_STEPS) - 1]


def _occupancy_colorbar(dark: bool = False) -> go.Scatter:
    """Traza sin puntos que solo dibuja la escala de colores de la ocupación de las rutas."""
    bounds = OCCUPANCY_STEPS + [1.0]
    scale = []
    for k, color in enumerate(_ramp(dark)):
        scale += [[bounds[k], color], [bounds[k + 1], color]]
    return go.Scatter(
        x=[None], y=[None], mode="markers", showlegend=False, hoverinfo="skip",
        marker=dict(colorscale=scale, cmin=0, cmax=1, color=[0], showscale=True,
                    colorbar=dict(title=dict(text="Ocupación", side="right"), tickformat=".0%", tickvals=bounds,
                                  thickness=10, len=0.6, outlinewidth=0)))


def solution_figure(problem: ProblemSBRP, solution, title=None, highlight_route: int = None,
                    show_students=False, height=520, dark: bool = False) -> go.Figure:
    """
    Rutas de la solución coloreadas por ocupación (azul más oscuro = más llena), con su escala de colores.
    highlight_route (1..R) resalta una ruta.
    """
    fig = go.Figure()
    for i, route in enumerate(solution.get_representation(), 1):
        stops = route_stops(route)
        if not stops:
            continue
        load = sum(s.num_assigned_students for s in stops)
        occupancy = load / problem.bus_capacity
        path = [problem.school] + stops + [problem.school]
        highlighted = highlight_route == i
        dimmed = highlight_route is not None and not highlighted
        fig.add_trace(go.Scatter(
            x=[p.coordinates[0] for p in path], y=[p.coordinates[1] for p in path], mode="lines",
            line=dict(width=4 if highlighted else 2,
                      color=HIGHLIGHT if highlighted else ("rgba(154,152,144,0.35)" if dimmed else _load_color(occupancy, dark))),
            name=f"Ruta {i}", showlegend=False,
            hovertemplate=f"Ruta {i}<br>{len(stops)} paradas<br>{load}/{problem.bus_capacity} estudiantes "
                          f"({occupancy:.0%})<extra></extra>"))
    for trace in _points_traces(problem, show_students, False, dark):
        fig.add_trace(trace)
    fig.add_trace(_occupancy_colorbar(dark))
    return _base_layout(fig, title, height)


def edge_origin_figure(problem: ProblemSBRP, solution, origin: dict, title=None, height=420, labels: dict = None,
                       dark: bool = False) -> go.Figure:
    """
    Aristas de la solución coloreadas según su origen (padre A, padre B, común o nueva). El trazo también
    cambia con el origen, para distinguirlas sin depender del color.
    """
    labels = {**EDGE_LABELS, **(labels or {})}
    coords = {problem.school.id: problem.school.coordinates}
    coords.update({s.id: s.coordinates for s in problem.stops})
    fig = go.Figure()
    for kind in ["AB", "A", "B", "nueva"]:
        xs, ys = [], []
        for (u, v), k in origin.items():
            if k == kind:
                xs += [coords[u][0], coords[v][0], None]
                ys += [coords[u][1], coords[v][1], None]
        if xs:
            fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name=f"{labels[kind]} ({len(xs) // 3})",
                                     line=dict(color=EDGE_COLORS[kind], dash=EDGE_DASH[kind],
                                               width=1.5 if kind == "AB" else 2.5),
                                     hoverinfo="skip"))
    for trace in _points_traces(problem, False, False, dark):
        trace.showlegend = False
        fig.add_trace(trace)
    return _base_layout(fig, title, height)


def convergence_figure(history: pd.DataFrame, height=300) -> go.Figure:
    """Mejor aptitud de la población y media de las factibles por generación (un solo eje: distancia)."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=history["generación"], y=history["mejor"], mode="lines", name="Mejor de la población",
                             line=dict(color=SERIES[0], width=2), hovertemplate="%{y:.2f}"))
    fig.add_trace(go.Scatter(x=history["generación"], y=history["media"], mode="lines", name="Media de las factibles",
                             line=dict(color=SERIES[1], width=2), hovertemplate="%{y:.2f}"))
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), hovermode="x unified",
                      legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0),
                      xaxis_title="Generación", yaxis_title="Distancia total")
    return fig


def percentage_figure(history: pd.DataFrame, column: str, label: str, height=220, fixed_range=True) -> go.Figure:
    fig = go.Figure(go.Scatter(x=history["generación"], y=history[column], mode="lines", name=label,
                               line=dict(color=SERIES[0], width=2),
                               hovertemplate="Generación %{x}<br>" + label + ": %{y:.0%}<extra></extra>"))
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=30, b=10), title=label, showlegend=False,
                      yaxis=dict(tickformat=".0%", range=[0, 1.05] if fixed_range else None, rangemode="tozero"),
                      xaxis_title="Generación")
    return fig


def rate_figure(history: pd.DataFrame, columns: dict, title: str, yaxis_title: str, height=260) -> go.Figure:
    """Varias series de la misma magnitud por generación ({columna: nombre}), en un solo eje."""
    fig = go.Figure()
    for k, (column, name) in enumerate(columns.items()):
        fig.add_trace(go.Scatter(x=history["generación"], y=history[column], mode="lines", name=name,
                                 line=dict(color=SERIES[k], width=2), hovertemplate="%{y:.2f}"))
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=60, b=10), title=title, hovermode="x unified",
                      legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0), showlegend=len(columns) > 1,
                      yaxis=dict(rangemode="tozero", title=yaxis_title), xaxis_title="Generación")
    return fig
