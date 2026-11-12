import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import common
import experiment
import widgets
from src.analysis import best_known

st.title("Comparar configuraciones")
st.caption("Ejecuta varias configuraciones con varias semillas sobre una instancia y compara sus resultados. "
           "Las corridas se ejecutan en paralelo en procesos independientes.")

configs = common.list_configs()
MAX_CONFIGS = len(common.SERIES_ALL)

RUN_COLUMNS = {
    "config": st.column_config.TextColumn("Configuración"),
    "seed": st.column_config.NumberColumn("Semilla"),
    "fitness": st.column_config.NumberColumn("Distancia", format="%.2f"),
    "gap": st.column_config.NumberColumn("Gap", format="percent", help="Cuánto peor que el mejor valor conocido."),
    "best_iteration": st.column_config.NumberColumn("Generación de la mejor"),
    "time": st.column_config.NumberColumn("Tiempo (s)", format="%.1f"),
    "stop_reason": st.column_config.TextColumn("Parada"),
    "generations": st.column_config.NumberColumn("Generaciones"),
    "feasible": st.column_config.CheckboxColumn("Factible"),
    "routes": st.column_config.NumberColumn("Rutas"),
}


def runs_frame(results, instance=None) -> pd.DataFrame:
    runs = pd.DataFrame([{k: v for k, v in r.items() if k != "history"} for r in results])
    if not runs.empty:
        runs["stop_reason"] = runs["stop_reason"].map(lambda r: common.STOP_REASONS.get(r, r))
        reference = best_known.reference(instance) if instance else None
        runs.insert(3, "gap", runs["fitness"] / reference["best_known"] - 1 if reference else float("nan"))
    return runs


# ------------------------- Parámetros -------------------------
with st.sidebar:
    st.header("Experimento")
    instance_label, instance_path = widgets.instance_select()
    selected = st.multiselect(f"Configuraciones (máx. {MAX_CONFIGS})", list(configs),
                              default=[c for c in ("config7", "config8", "config9") if c in configs],
                              max_selections=MAX_CONFIGS,
                              help="Cada configuración tiene un color fijo, en el orden en que se eligen.")
    seeds = st.number_input("Semillas por configuración", 1, 100, 3,
                            help="Cada configuración se ejecuta con las semillas 1..N, así las corridas son reproducibles "
                                 "y todas las configuraciones usan las mismas semillas.")
    st.subheader("Presupuesto común")
    population_size = st.number_input("Población (0 = la de cada config)", 0, 5000, 100, step=10,
                                      help="El mismo tamaño de población para todas las configuraciones.")
    max_iter = st.number_input("Máx. generaciones (0 = la de cada config)", 0, 5000, 30)
    fixed_budget = st.toggle("Desactivar la parada por estancamiento", value=True,
                             help="Todas las corridas usan el mismo número de generaciones, para comparar en igualdad.")
    workers = st.number_input("Procesos en paralelo", 1, os.cpu_count() or 1, min(4, os.cpu_count() or 1),
                              help=f"Corridas simultáneas. Este equipo tiene {os.cpu_count()} núcleos.")

    problems = []
    if not selected:
        problems.append("Elige al menos una configuración.")
    for name in selected:
        config = common.read_config(configs[name])
        population = int(population_size) or int(config["initial_population_size"])
        if "tournament_size" in config and population <= int(config["tournament_size"]):
            problems.append(f"{name}: la población ({population}) debe ser mayor que su tamaño de torneo "
                            f"({config['tournament_size']}).")
    total = len(selected) * int(seeds)
    run = st.button(f"▶ Comparar ({total} corridas)" if total else "▶ Comparar", type="primary", width="stretch",
                    disabled=bool(problems))
    for problem_text in problems:
        st.error(problem_text)

# ------------------------- Ejecución -------------------------
if run:
    overrides = {}
    if population_size:
        overrides["initial_population_size"] = int(population_size)
    if max_iter:
        overrides["max_iter"] = int(max_iter)
    if fixed_budget:
        overrides["max_stagnation_iter"] = int(max_iter) if max_iter else 10 ** 6

    jobs = [(name, str(configs[name]), str(instance_path), seed, overrides)
            for name in selected for seed in range(1, int(seeds) + 1)]
    progress = st.progress(0.0, text=f"0/{len(jobs)} corridas · iniciando procesos…")
    st.caption("Cambiar cualquier control durante la comparación la interrumpe.")
    table_placeholder = st.empty()
    results, failures = [], []
    start = time.time()
    with ProcessPoolExecutor(max_workers=int(workers)) as pool:
        futures = {pool.submit(experiment.run_once, *job): job for job in jobs}
        for done, future in enumerate(as_completed(futures), 1):
            name, _, _, seed, _ = futures[future]
            try:
                results.append(future.result())
            except Exception as error:
                failures.append(f"{name} (semilla {seed}): {error}")
            progress.progress(done / len(jobs), text=f"{done}/{len(jobs)} corridas · {time.time() - start:.0f} s")
            table_placeholder.dataframe(runs_frame(results, instance_label), hide_index=True, width="stretch",
                                        column_config=RUN_COLUMNS)
    progress.empty()
    table_placeholder.empty()
    st.session_state["compare"] = {"results": results, "failures": failures, "instance": instance_label,
                                   "order": selected, "time": time.time() - start,
                                   "budget": (int(population_size), int(max_iter), fixed_budget)}
    st.rerun()

# ------------------------- Resultados -------------------------
data = st.session_state.get("compare")
if data is None:
    st.info("Elige la instancia, las configuraciones y el número de semillas en la barra lateral y pulsa **Comparar**. "
            "Por defecto todas las corridas usan la misma población y el mismo número de generaciones.")
    st.stop()

if data["failures"]:
    st.error(f"Fallaron {len(data['failures'])} corridas:\n\n" + "\n".join(f"- {f}" for f in data["failures"]))
if not data["results"]:
    st.stop()

runs = runs_frame(data["results"], data["instance"])
order = [c for c in data["order"] if c in set(runs["config"])]
colors = {name: common.SERIES_ALL[i] for i, name in enumerate(order)}

summary = runs.groupby("config").agg(
    corridas=("fitness", "size"), media=("fitness", "mean"), desviación=("fitness", "std"), mejor=("fitness", "min"),
    peor=("fitness", "max"), factibles=("feasible", "mean"), generación_mejor=("best_iteration", "mean"),
    tiempo_medio=("time", "mean")).reindex(order)
best_mean = summary["media"].min()
summary.insert(2, "vs la mejor", (summary["media"] - best_mean) / best_mean)
reference = best_known.reference(data["instance"])
summary.insert(3, "gap", summary["media"] / reference["best_known"] - 1 if reference else float("nan"))
summary = summary.reset_index()

st.subheader(f"Resultados · {common.instance_name(data['instance'])} · {len(runs)} corridas en {data['time']:.0f} s")
budget_population, budget_iter, budget_fixed = data.get("budget", (0, 0, False))
st.caption(f"Población: {budget_population or 'la de cada configuración'} · "
           f"máx. generaciones: {budget_iter or 'las de cada configuración'} · "
           f"parada por estancamiento: {'desactivada' if budget_fixed else 'la de cada configuración'}.")
if data["instance"] != st.session_state.get(widgets.INSTANCE_KEY):
    st.info(f"Estos resultados son de {common.instance_name(data['instance'])}; la instancia elegida ahora es otra. "
            "Pulsa **Comparar** para ejecutarla.")
best_name = summary.loc[summary["media"].idxmin(), "config"] if summary["media"].notna().any() else None
if best_name is not None and len(order) > 1:
    st.markdown(f"Mejor distancia media: **{best_name}** ({best_mean:.2f}).")
if reference:
    st.caption(f"Mejor conocido de la instancia: {common.best_known_text(data['instance'])}.")
st.dataframe(summary, hide_index=True, width="stretch", column_config={
    "config": st.column_config.TextColumn("Configuración"),
    "corridas": st.column_config.NumberColumn("Corridas"),
    "media": st.column_config.NumberColumn("Distancia media", format="%.2f"),
    "desviación": st.column_config.NumberColumn("Desviación", format="%.2f",
                                                help="Desviación estándar entre semillas (vacía con una sola semilla)."),
    "mejor": st.column_config.NumberColumn("Mejor", format="%.2f"),
    "peor": st.column_config.NumberColumn("Peor", format="%.2f"),
    "gap": st.column_config.NumberColumn(
        "Gap medio", format="percent",
        help="Cuánto peor es la distancia media que el mejor valor conocido de la instancia (0% = lo iguala)."),
    "vs la mejor": st.column_config.NumberColumn(
        "vs la mejor media", format="percent",
        help="Cuánto peor es la distancia media que la de la mejor configuración (0% = la mejor)."),
    "factibles": st.column_config.NumberColumn("Factibles", format="percent",
                                               help="Fracción de corridas cuya mejor solución es factible."),
    "generación_mejor": st.column_config.NumberColumn("Generación de la mejor (media)", format="%.1f",
                                                      help="Generación media en la que se encontró la mejor solución. "
                                                           "Si está cerca del final, más generaciones podrían mejorar."),
    "tiempo_medio": st.column_config.NumberColumn("Tiempo medio (s)", format="%.1f"),
})

left, right = st.columns(2)
box = go.Figure()
for name in order:
    values = runs.loc[runs["config"] == name, "fitness"]
    box.add_trace(go.Box(y=values, name=name, marker_color=colors[name], boxpoints="all", jitter=0.3, pointpos=0,
                         hovertemplate=f"{name}<br>%{{y:.2f}}<extra></extra>"))
if reference:
    box.add_hline(y=reference["best_known"], line_dash="dot", line_color=common.REFERENCE_LINE,
                  annotation_text="Mejor conocido", annotation_position="top left")
box.update_layout(title="Distancia final por configuración (cada punto, una semilla)", height=380, showlegend=False,
                  margin=dict(l=10, r=10, t=40, b=10), yaxis_title="Distancia total")
left.plotly_chart(box, width="stretch")

curves = go.Figure()
for name in order:
    histories = [r["history"] for r in data["results"] if r["config"] == name and r["history"]]
    if not histories:
        continue
    length = max(len(h) for h in histories)
    # Las corridas que terminan antes conservan su último valor; las generaciones sin solución factible se ignoran
    padded = pd.DataFrame([h + [h[-1]] * (length - len(h)) for h in histories], dtype=float)
    curves.add_trace(go.Scatter(x=list(range(length)), y=padded.mean().tolist(), mode="lines", name=name,
                                line=dict(color=colors[name], width=2), hovertemplate="%{y:.2f}"))
if reference:
    curves.add_hline(y=reference["best_known"], line_dash="dot", line_color=common.REFERENCE_LINE,
                     annotation_text="Mejor conocido", annotation_position="top left")
curves.update_layout(title="Mejor distancia encontrada (media de las semillas)", height=380, hovermode="x unified",
                     margin=dict(l=10, r=10, t=70, b=10), xaxis_title="Generación", yaxis_title="Distancia total",
                     legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0))
right.plotly_chart(curves, width="stretch")

with st.expander("Detalle de configuraciones"):
    st.caption("Valores de los archivos de configuración; el presupuesto común de la barra lateral los sustituye "
               "durante la comparación.")
    details = pd.DataFrame({name: common.read_config(configs[name]) for name in order}).drop(index="instance_path",
                                                                                             errors="ignore")
    st.dataframe(details.astype(str), width="stretch")

with st.expander("Todas las corridas"):
    st.dataframe(runs, hide_index=True, width="stretch", column_config=RUN_COLUMNS)
    st.download_button("Descargar CSV", runs.to_csv(index=False).encode("utf-8"), "comparacion.csv", "text/csv")
