import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import common
import experiment

st.title("Comparar configuraciones")
st.caption("Ejecuta varias configuraciones con varias semillas sobre una instancia y compara sus resultados. "
           "Las corridas se ejecutan en paralelo en procesos independientes.")

instances, configs = common.list_instances(), common.list_configs()
MAX_CONFIGS = len(common.SERIES_ALL)

# ------------------------- Parámetros -------------------------
with st.sidebar:
    st.header("Experimento")
    instance_label = st.selectbox("Instancia", list(instances),
                                  index=list(instances).index("real/inst54-7s20-100-c50-w20.xpress")
                                  if "real/inst54-7s20-100-c50-w20.xpress" in instances else 0)
    selected = st.multiselect(f"Configuraciones (máx. {MAX_CONFIGS})", list(configs),
                              default=[c for c in ("config7", "config8", "config9") if c in configs],
                              max_selections=MAX_CONFIGS)
    seeds = st.number_input("Semillas por configuración", 1, 100, 3)
    st.subheader("Presupuesto común")
    population_size = st.number_input("Población (0 = la de cada config)", 0, 5000, 100, step=10)
    max_iter = st.number_input("Máx. generaciones (0 = la de cada config)", 0, 5000, 30)
    fixed_budget = st.toggle("Desactivar la parada por estancamiento", value=True,
                             help="Todas las corridas usan el mismo número de generaciones, para comparar en igualdad.")
    workers = st.number_input("Procesos en paralelo", 1, os.cpu_count() or 1, min(4, os.cpu_count() or 1))
    run = st.button("▶ Comparar", type="primary", width="stretch", disabled=not selected)

# ------------------------- Ejecución -------------------------
if run:
    overrides = {}
    if population_size:
        overrides["initial_population_size"] = int(population_size)
    if max_iter:
        overrides["max_iter"] = int(max_iter)
    if fixed_budget:
        overrides["max_stagnation_iter"] = int(max_iter) if max_iter else 10 ** 6

    jobs = [(name, str(configs[name]), str(instances[instance_label]), seed, overrides)
            for name in selected for seed in range(1, int(seeds) + 1)]
    progress = st.progress(0.0, text=f"0/{len(jobs)} corridas")
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
            table_placeholder.dataframe(pd.DataFrame([{k: v for k, v in r.items() if k != "history"} for r in results]),
                                        hide_index=True, width="stretch")
    progress.empty()
    table_placeholder.empty()
    st.session_state["compare"] = {"results": results, "failures": failures, "instance": instance_label,
                                   "order": selected, "time": time.time() - start}
    st.rerun()

# ------------------------- Resultados -------------------------
data = st.session_state.get("compare")
if data is None:
    st.info("Elige la instancia, las configuraciones y el número de semillas en la barra lateral y pulsa **Comparar**. "
            "Por defecto todas las corridas usan la misma población y el mismo número de generaciones.")
    st.stop()

for failure in data["failures"]:
    st.error(f"Falló la corrida {failure}")
if not data["results"]:
    st.stop()

runs = pd.DataFrame([{k: v for k, v in r.items() if k != "history"} for r in data["results"]])
order = [c for c in data["order"] if c in set(runs["config"])]
colors = {name: common.SERIES_ALL[i] for i, name in enumerate(order)}

summary = runs.groupby("config").agg(
    corridas=("fitness", "size"), media=("fitness", "mean"), desviación=("fitness", "std"), mejor=("fitness", "min"),
    peor=("fitness", "max"), factibles=("feasible", "mean"), generación_mejor=("best_iteration", "mean"),
    tiempo_medio=("time", "mean")).reindex(order)
best_mean = summary["media"].min()
summary.insert(2, "vs la mejor", (summary["media"] - best_mean) / best_mean)
summary = summary.reset_index()

st.subheader(f"Resultados · {data['instance']} · {len(runs)} corridas en {data['time']:.0f} s")
st.dataframe(summary, hide_index=True, width="stretch", column_config={
    "media": st.column_config.NumberColumn("Distancia media", format="%.2f"),
    "desviación": st.column_config.NumberColumn("Desviación", format="%.2f"),
    "mejor": st.column_config.NumberColumn("Mejor", format="%.2f"),
    "peor": st.column_config.NumberColumn("Peor", format="%.2f"),
    "vs la mejor": st.column_config.NumberColumn("vs la mejor media", format="percent"),
    "factibles": st.column_config.NumberColumn("Factibles", format="percent"),
    "generación_mejor": st.column_config.NumberColumn("Generación de la mejor (media)", format="%.1f"),
    "tiempo_medio": st.column_config.NumberColumn("Tiempo medio (s)", format="%.1f"),
})

left, right = st.columns(2)
box = go.Figure()
for name in order:
    values = runs.loc[runs["config"] == name, "fitness"]
    box.add_trace(go.Box(y=values, name=name, marker_color=colors[name], boxpoints="all", jitter=0.3, pointpos=0,
                         hovertemplate=f"{name}<br>%{{y:.2f}}<extra></extra>"))
box.update_layout(title="Distancia final por configuración", height=380, showlegend=False,
                  margin=dict(l=10, r=10, t=40, b=10), yaxis_title="Distancia")
left.plotly_chart(box, width="stretch")

curves = go.Figure()
for name in order:
    histories = [r["history"] for r in data["results"] if r["config"] == name and r["history"]]
    length = max(len(h) for h in histories)
    padded = [h + [h[-1]] * (length - len(h)) for h in histories]
    mean_curve = [sum(values) / len(values) for values in zip(*padded)]
    curves.add_trace(go.Scatter(x=list(range(length)), y=mean_curve, mode="lines", name=name,
                                line=dict(color=colors[name], width=2)))
curves.update_layout(title="Mejor distancia encontrada (media de las semillas)", height=380, hovermode="x unified",
                     margin=dict(l=10, r=10, t=40, b=10), xaxis_title="Generación", yaxis_title="Distancia",
                     legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0))
right.plotly_chart(curves, width="stretch")

with st.expander("Detalle de configuraciones"):
    details = pd.DataFrame({name: common.read_config(configs[name]) for name in order}).drop(index="instance_path",
                                                                                             errors="ignore")
    st.dataframe(details.astype(str), width="stretch")

with st.expander("Todas las corridas"):
    st.dataframe(runs, hide_index=True, width="stretch")
    st.download_button("Descargar CSV", runs.to_csv(index=False).encode("utf-8"), "comparacion.csv", "text/csv")
