import ast
import re
from pathlib import Path

import pandas as pd
import streamlit as st

import common
from src.problems.problem_sbrp.data_io.file_data_input_sbrp import FileDataInputSBRP
from src.problems.problem_sbrp.model.route import Route
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP

st.title("Resultados guardados")
st.caption("Explora los resultados que genera app/main.py (results/config<N>/<instancia>/run_<k>.csv). "
           "Los resultados antiguos, sin columna de factibilidad, se pueden revalidar con el validador actual.")

ROUTE_PATTERN = re.compile(r"Ruta(\d+)\[(.*?)\]")


# ------------------------- Lectura -------------------------
@st.cache_data(show_spinner="Leyendo resultados…")
def load_runs(results_dir: str) -> pd.DataFrame:
    rows = []
    for csv_path in Path(results_dir).glob("config*/*/run_*.csv"):
        try:
            data = pd.read_csv(csv_path)
        except Exception as error:
            rows.append({"config": csv_path.parts[-3], "instancia": csv_path.parts[-2], "archivo": str(csv_path),
                         "error": str(error)})
            continue
        for _, record in data.iterrows():
            run = record.to_dict()
            run.update({"config": csv_path.parts[-3], "instancia": csv_path.parts[-2],
                        "corrida": int(re.search(r"run_(\d+)", csv_path.name).group(1)), "archivo": str(csv_path)})
            rows.append(run)
    if not rows:
        return pd.DataFrame()
    runs = pd.DataFrame(rows)
    if "feasible" not in runs:
        runs["feasible"] = None
    runs["factibilidad"] = runs["feasible"].map({True: "Factible", False: "Infactible", "True": "Factible",
                                                 "False": "Infactible"}).fillna("Sin dato")
    return runs.sort_values(["config", "instancia", "corrida"],
                            key=lambda c: c.map(lambda v: tuple(common._natural_key(v))) if c.name != "corrida" else c)


def find_instance(name: str):
    matches = [path for label, path in common.list_instances().items() if Path(label).stem == name]
    return matches[0] if matches else None


def rebuild_solution(run: dict):
    """
    Reconstruye el problema (con la asignación guardada) y la solución a partir de las columnas del CSV.
    """
    instance_path = find_instance(run["instancia"])
    if instance_path is None:
        raise ValueError(f"No se encontró la instancia {run['instancia']} en data/instances")
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


# ------------------------- Carga y filtros -------------------------
results_dir = st.text_input("Carpeta de resultados", str(common.RESULTS_DIR))
if not Path(results_dir).is_dir():
    st.info(f"No existe la carpeta {results_dir}. Ejecuta app/main.py para generar resultados o indica otra carpeta.")
    st.stop()

runs = load_runs(results_dir)
if runs.empty:
    st.info("La carpeta no contiene resultados con la estructura config<N>/<instancia>/run_<k>.csv.")
    st.stop()
if "error" in runs:
    for _, failed in runs[runs["error"].notna()].iterrows():
        st.warning(f"No se pudo leer {failed['archivo']}: {failed['error']}")
    runs = runs[runs["error"].isna()]

c1, c2, c3 = st.columns([2, 3, 1])
configs = c1.multiselect("Configuraciones", sorted(runs["config"].unique(), key=common._natural_key))
instances = c2.multiselect("Instancias", sorted(runs["instancia"].unique(), key=common._natural_key))
c3.write("")
if c3.button("Recargar", width="stretch"):
    load_runs.clear()
    st.rerun()
mask = pd.Series(True, index=runs.index)
if configs:
    mask &= runs["config"].isin(configs)
if instances:
    mask &= runs["instancia"].isin(instances)
filtered = runs[mask]

st.metric("Corridas", len(filtered))
tab_summary, tab_runs, tab_detail = st.tabs(["Resumen", "Corridas", "Detalle de una corrida"])

with tab_summary:
    pivot = filtered.pivot_table(index="instancia", columns="config", values="value", aggfunc="mean")
    pivot = pivot.reindex(sorted(pivot.index, key=common._natural_key))
    pivot = pivot[sorted(pivot.columns, key=common._natural_key)]
    st.markdown("**Distancia media por instancia y configuración** (la menor de cada fila, resaltada)")
    st.dataframe(pivot.style.format("{:.2f}", na_rep="—").highlight_min(axis=1, color="#cde2fb"), width="stretch")
    feasibility = filtered.groupby(["config", "factibilidad"]).size().unstack(fill_value=0)
    st.markdown("**Factibilidad registrada por configuración**")
    st.dataframe(feasibility, width="stretch")

with tab_runs:
    columns = [c for c in ["config", "instancia", "corrida", "value", "iteration", "execution_time", "stop_reason",
                           "stop_iteration", "factibilidad", "violations"] if c in filtered]
    st.dataframe(filtered[columns], hide_index=True, width="stretch")

with tab_detail:
    options = filtered.index.tolist()
    choice = st.selectbox("Corrida", options, format_func=lambda i: f"{filtered.loc[i, 'config']} · "
                          f"{filtered.loc[i, 'instancia']} · run {filtered.loc[i, 'corrida']} · {filtered.loc[i, 'value']:.2f}")
    run = filtered.loc[choice].to_dict()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Distancia", f"{run['value']:.2f}")
    c2.metric("Encontrada en la generación", run.get("iteration"))
    c3.metric("Tiempo", f"{run.get('execution_time', 0):.1f} s")
    c4.metric("Factibilidad registrada", run["factibilidad"])

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
            st.caption(f"Distancia recalculada: {recomputed:.2f} (guardada: {run['value']:.2f})")
            routes = common.routes_table(problem, solution)
            st.dataframe(routes, hide_index=True, width="stretch",
                         column_config={"Ocupación": st.column_config.ProgressColumn(
                             "Ocupación", format="percent", min_value=0, max_value=1)})
        left.plotly_chart(common.solution_figure(problem, solution, height=480), width="stretch")
    except Exception as error:
        right.warning(f"No se pudo reconstruir la solución: {error}")
        image = Path(run["archivo"]).with_name(f"run_{run['corrida']}_result.png")
        if image.exists():
            left.image(str(image), caption="Imagen guardada por app/main.py")

    if isinstance(run.get("violations"), str) and run["violations"]:
        st.warning(f"Violaciones registradas en el CSV: {run['violations']}")
