import ast
import json
import re
from pathlib import Path

import pandas as pd
import streamlit as st

import common
import widgets
from src.analysis import best_known
from src.problems.problem_sbrp.data_io.file_data_input_sbrp import FileDataInputSBRP
from src.problems.problem_sbrp.model.route import Route
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP

st.title("Resultados guardados")
st.caption("Explora los resultados que genera app/main.py: cada lanzamiento crea results/<fecha_hora>/ con "
           "config<N>/<instancia>/run_<k>.csv. Los resultados antiguos, sin columna de factibilidad, se pueden revalidar "
           "con el validador actual, y las corridas con semilla se pueden reproducir en vivo.")

ROOT_LAUNCH = "(carpeta raíz)"

ROUTE_PATTERN = re.compile(r"Ruta(\d+)\[(.*?)\]")


# ------------------------- Lectura -------------------------
@st.cache_data(show_spinner="Leyendo resultados…")
def load_runs(results_dir: str) -> pd.DataFrame:
    rows = []
    base = Path(results_dir)
    # Busca en la carpeta y en las carpetas de cada lanzamiento: <lanzamiento>/config<N>/<instancia>/run_<k>.csv
    for csv_path in base.rglob("run_*.csv"):
        if not csv_path.parent.parent.name.startswith("config"):
            continue
        launch_dir = csv_path.parents[2]
        launch = ROOT_LAUNCH if launch_dir == base else launch_dir.relative_to(base).as_posix()
        location = {"config": csv_path.parts[-3], "instancia": csv_path.parts[-2], "lanzamiento": launch,
                    "carpeta_lanzamiento": str(launch_dir), "archivo": str(csv_path)}
        try:
            data = pd.read_csv(csv_path)
        except Exception as error:
            rows.append({**location, "error": str(error)})
            continue
        for _, record in data.iterrows():
            run = record.to_dict()
            run.update({**location, "corrida": int(re.search(r"run_(\d+)", csv_path.name).group(1))})
            rows.append(run)
    if not rows:
        return pd.DataFrame()
    runs = pd.DataFrame(rows)
    if "feasible" not in runs:
        runs["feasible"] = None
    runs["factibilidad"] = runs["feasible"].map({True: "Factible", False: "Infactible", "True": "Factible",
                                                 "False": "Infactible"}).fillna("Sin dato")
    for column in ("value", "iteration", "execution_time"):
        runs[column] = pd.to_numeric(runs[column], errors="coerce") if column in runs else float("nan")
    # Mejor valor conocido de cada instancia y gap de la corrida respecto a él
    runs["mejor_conocido"] = runs["instancia"].map(lambda i: (best_known.reference(i) or {}).get("best_known"))
    runs["mejor_conocido"] = pd.to_numeric(runs["mejor_conocido"], errors="coerce")
    runs["gap"] = runs["value"] / runs["mejor_conocido"] - 1
    if "stop_reason" in runs:
        runs["stop_reason"] = runs["stop_reason"].map(lambda r: common.STOP_REASONS.get(r, r))
    return runs.sort_values(["lanzamiento", "config", "instancia", "corrida"],
                            key=lambda c: c.map(lambda v: tuple(common._natural_key(v))) if c.name != "corrida" else c)


def read_manifest(launch_dir: str):
    path = Path(launch_dir) / "manifest.json"
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def find_instance(run: dict):
    """Instancia de la corrida: la registrada en el manifiesto del lanzamiento o, si no hay, la de data/instances."""
    manifest = read_manifest(run["carpeta_lanzamiento"])
    if manifest and run["instancia"] in manifest.get("instances", {}):
        path = Path(manifest["instances"][run["instancia"]])
        path = path if path.is_absolute() else common.ROOT / path
        if path.exists():
            return path
    matches = [path for label, path in common.list_instances().items() if Path(label).stem == run["instancia"]]
    return matches[0] if matches else None


def replay_request(run: dict):
    """Datos para reproducir la corrida en vivo, o None si no registra semilla o configuración."""
    manifest = read_manifest(run["carpeta_lanzamiento"])
    seed = run.get("seed")
    if manifest is None or seed is None or pd.isna(seed) or run["config"] not in manifest.get("configs", {}):
        return None
    instance_path = find_instance(run)
    if instance_path is None:
        return None
    return {"config_path": str(Path(run["carpeta_lanzamiento"]) / manifest["configs"][run["config"]]),
            "instance_path": str(instance_path), "seed": int(seed), "original": None if pd.isna(run["value"]) else run["value"],
            "label": f"{run['config']} · {run['instancia']} · run {run['corrida']} ({run['lanzamiento']})"}


def rebuild_solution(run: dict):
    """
    Reconstruye el problema (con la asignación guardada) y la solución a partir de las columnas del CSV.
    """
    instance_path = find_instance(run)
    if instance_path is None:
        raise ValueError(f"No se encontró la instancia {run['instancia']}")
    problem = ProblemSBRP()
    problem.construct(FileDataInputSBRP(str(instance_path)).conform())
    stops = {stop.id: stop for stop in problem.stops}
    students = {student.id: student for student in problem.students}

    for stop_name, student_names in ast.literal_eval(run["student_assignments"]).items():
        stop = stops[int(stop_name.replace("Stop", ""))]
        for student_name in student_names:
            students[int(student_name.replace("student", ""))].assigned_stop = stop
            stop.num_assigned_students += 1

    routes = []
    for _, content in ROUTE_PATTERN.findall(run["routes"]):
        names = [name.strip() for name in content.split(",") if name.strip()]
        routes.append(Route(stops=[problem.school if name == "School" else stops[int(name.replace("Stop", ""))]
                                   for name in names]))
    return problem, SolutionRouteSBRP(routes=routes)


def fmt(value, pattern="{:.2f}", empty="—"):
    """Formatea un valor numérico del CSV, que puede faltar."""
    return empty if value is None or pd.isna(value) else pattern.format(value)


# ------------------------- Carga y filtros -------------------------
c1, c2 = st.columns([5, 1], vertical_alignment="bottom")
results_dir = c1.text_input("Carpeta de resultados", str(common.RESULTS_DIR),
                            help="Carpeta donde app/main.py crea un lanzamiento por ejecución (<fecha_hora>/config<N>/...). "
                                 "También se leen resultados antiguos con config<N>/ directamente en la carpeta.")
if c2.button("Recargar", width="stretch", help="Vuelve a leer los CSV (por ejemplo, tras una nueva ejecución)."):
    load_runs.clear()
    st.rerun()
if not Path(results_dir).is_dir():
    st.info(f"No existe la carpeta {results_dir}. Ejecuta app/main.py para generar resultados o indica otra carpeta.")
    st.stop()

runs = load_runs(results_dir)
if runs.empty:
    st.info("La carpeta no contiene resultados con la estructura [<lanzamiento>/]config<N>/<instancia>/run_<k>.csv.")
    st.stop()
if "error" in runs:
    for _, failed in runs[runs["error"].notna()].iterrows():
        st.warning(f"No se pudo leer {failed['archivo']}: {failed['error']}")
    runs = runs[runs["error"].isna()]
    if runs.empty:
        st.stop()

# Lanzamientos del más reciente al más antiguo (el nombre de la carpeta es su fecha y hora); la carpeta raíz al final
launches = sorted((l for l in runs["lanzamiento"].unique() if l != ROOT_LAUNCH), key=lambda l: Path(l).name, reverse=True)
launches += [ROOT_LAUNCH] if ROOT_LAUNCH in set(runs["lanzamiento"]) else []
c0, c1, c2 = st.columns([2, 2, 3])
launch = c0.selectbox("Lanzamiento", ["Todos"] + launches, index=1 if launches else 0,
                      help="Cada ejecución de app/main.py es un lanzamiento (carpeta <fecha_hora>). "
                           "Por defecto se muestra el más reciente.")
if launch != "Todos":
    runs = runs[runs["lanzamiento"] == launch]
configs = c1.multiselect("Configuraciones", sorted(runs["config"].unique(), key=common._natural_key),
                         placeholder="Todas")
instances = c2.multiselect("Instancias", sorted(runs["instancia"].unique(), key=common._natural_key),
                           placeholder="Todas")
mask = pd.Series(True, index=runs.index)
if configs:
    mask &= runs["config"].isin(configs)
if instances:
    mask &= runs["instancia"].isin(instances)
filtered = runs[mask]

st.caption(f"{len(filtered)} de {len(runs)} corridas · {filtered['config'].nunique()} configuraciones · "
           f"{filtered['instancia'].nunique()} instancias")
if filtered.empty:
    st.info("Ninguna corrida cumple los filtros: esas configuraciones no se ejecutaron sobre esas instancias.")
    st.stop()

tab_summary, tab_runs, tab_detail = st.tabs(["Resumen", "Corridas", "Detalle de una corrida"])

with tab_summary:
    pivot = filtered.pivot_table(index="instancia", columns="config", values="value", aggfunc="mean")
    pivot = pivot.reindex(sorted(pivot.index, key=common._natural_key))
    pivot = pivot[sorted(pivot.columns, key=common._natural_key)]
    st.markdown("**Distancia media por instancia y configuración** (la menor de cada fila, en negrita y resaltada)")
    # Texto oscuro explícito para que el resaltado se lea también con el tema oscuro
    st.dataframe(pivot.style.format("{:.2f}", na_rep="—").highlight_min(
        axis=1, props=f"background-color: {common.TABLE_HIGHLIGHT}; color: #0b0b0b; font-weight: bold"), width="stretch")
    if filtered["gap"].notna().any():
        gaps = filtered.pivot_table(index="instancia", columns="config", values="gap", aggfunc="mean")
        gaps = gaps.reindex(sorted(gaps.index, key=common._natural_key))
        gaps = gaps[sorted(gaps.columns, key=common._natural_key)]
        gaps.loc["Media"] = gaps.mean()
        st.markdown("**Gap medio sobre el mejor conocido** (0% = iguala el mejor valor conocido; negativo = lo mejora)")
        st.dataframe(gaps.style.format("{:+.1%}", na_rep="—").highlight_min(
            axis=1, props=f"background-color: {common.TABLE_HIGHLIGHT}; color: #0b0b0b; font-weight: bold"),
            width="stretch")
        st.caption("Mejores conocidos: óptimos y soluciones de Schittekat et al. (2013) y de la tesis de Pérez Pérez "
                   "(2020). Ver data/instances/best_known.csv.")
    feasibility = filtered.groupby(["config", "factibilidad"]).size().unstack(fill_value=0)
    feasibility = feasibility.reindex(columns=[c for c in ("Factible", "Infactible", "Sin dato") if c in feasibility])
    st.markdown("**Factibilidad registrada por configuración** (número de corridas)")
    st.dataframe(feasibility, width="stretch")
    if "Sin dato" in feasibility:
        st.caption("«Sin dato»: resultados antiguos sin columna de factibilidad. Revalídalos en «Detalle de una corrida».")

with tab_runs:
    columns = [c for c in ["config", "instancia", "corrida", "value", "mejor_conocido", "gap", "iteration", "execution_time", "stop_reason",
                           "stop_iteration", "factibilidad", "violations"] if c in filtered]
    st.dataframe(filtered[columns], hide_index=True, width="stretch", column_config={
        "config": st.column_config.TextColumn("Configuración"),
        "instancia": st.column_config.TextColumn("Instancia"),
        "corrida": st.column_config.NumberColumn("Corrida"),
        "value": st.column_config.NumberColumn("Distancia", format="%.2f"),
        "mejor_conocido": st.column_config.NumberColumn("Mejor conocido", format="%.2f"),
        "gap": st.column_config.NumberColumn("Gap", format="percent",
                                             help="Cuánto peor que el mejor valor conocido (0% = lo iguala)."),
        "iteration": st.column_config.NumberColumn("Generación de la mejor"),
        "execution_time": st.column_config.NumberColumn("Tiempo (s)", format="%.1f"),
        "stop_reason": st.column_config.TextColumn("Parada"),
        "stop_iteration": st.column_config.NumberColumn("Generaciones"),
        "factibilidad": st.column_config.TextColumn("Factibilidad registrada"),
        "violations": st.column_config.TextColumn("Violaciones registradas"),
    })

with tab_detail:
    options = filtered.index.tolist()
    choice = st.selectbox("Corrida", options, format_func=lambda i: f"{filtered.loc[i, 'config']} · "
                          f"{filtered.loc[i, 'instancia']} · run {filtered.loc[i, 'corrida']} · "
                          f"{fmt(filtered.loc[i, 'value'])}")
    run = filtered.loc[choice].to_dict()
    request = replay_request(run)
    if request:
        if st.button("▶ Reproducir en vivo", type="primary",
                     help="Abre «Ejecutar en vivo» con la configuración guardada y la semilla de esta corrida, "
                          "para ver generación a generación cómo se llegó a este resultado."):
            st.session_state["replay_request"] = request
            st.switch_page("views/live_run.py")
    else:
        st.caption("Esta corrida no se puede reproducir: no registra semilla o su lanzamiento no tiene manifest.json "
                   "(resultados anteriores a la ejecución por lanzamientos).")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Distancia", fmt(run["value"]),
              delta=f"{run['gap']:+.1%} sobre el mejor conocido" if pd.notna(run.get("gap")) else None,
              delta_color="inverse", help=f"Mejor conocido: {common.best_known_text(run['instancia']) or 'sin dato'}")
    c2.metric("Encontrada en la generación", fmt(run.get("iteration"), "{:.0f}"))
    c3.metric("Tiempo", fmt(run.get("execution_time"), "{:.1f} s"))
    c4.metric("Factibilidad registrada", run["factibilidad"],
              help="La que guardó app/main.py al ejecutar. Puede diferir de la revalidación si el validador cambió.")

    left, right = st.columns([3, 2])
    try:
        problem, solution = rebuild_solution(run)
        violations = problem.violations(solution)
        recomputed = problem.objective_function(solution)
        with right:
            st.markdown("**Revalidación con el validador actual**")
            if violations:
                st.error("Infactible: " + "; ".join(violations))
            else:
                st.success("Factible")
            if pd.notna(run["value"]) and abs(recomputed - run["value"]) > 1e-6:
                st.warning(f"La distancia recalculada ({recomputed:.2f}) no coincide con la guardada ({fmt(run['value'])}).")
            else:
                st.caption(f"Distancia recalculada: {recomputed:.2f} (coincide con la guardada).")
            routes = common.routes_table(problem, solution)
            st.dataframe(routes, hide_index=True, width="stretch",
                         column_config={"Ocupación": st.column_config.ProgressColumn(
                             "Ocupación", format="percent", min_value=0, max_value=1),
                             "Distancia": st.column_config.NumberColumn("Distancia", format="%.2f")})
        left.plotly_chart(common.solution_figure(problem, solution, height=480, dark=widgets.is_dark()),
                          width="stretch", alt=f"Mapa de las {len(routes)} rutas de la corrida.")
    except Exception as error:
        right.warning(f"No se pudo reconstruir la solución: {error}")
        image = Path(run["archivo"]).with_name(f"run_{run['corrida']}_result.png")
        if image.exists():
            left.image(str(image), caption="Imagen guardada por app/main.py")

    if isinstance(run.get("violations"), str) and run["violations"]:
        st.warning(f"Violaciones registradas en el CSV: {run['violations']}")
