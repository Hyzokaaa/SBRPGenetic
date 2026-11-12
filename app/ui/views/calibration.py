import json
import os
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import common
import widgets
from src.analysis import grid_analysis

st.title("Calibración de operadores")
st.caption("Analiza un experimento de rejilla (app/grid.py): todas las combinaciones de operadores con el mismo "
           "presupuesto. Las combinaciones se comparan por su gap sobre el mejor valor conocido de cada instancia.")

FACTOR_LABELS = {"stop_assign_strategy": "Asignación", "route_generator_strategy": "Generación de rutas",
                 "selection_operator": "Selección", "crossover_operator": "Cruce", "mutation_operator": "Mutación",
                 "replacement_operator": "Reemplazo", "diversity_operator": "Diversidad"}
ALPHA = 0.05


@st.cache_data(show_spinner="Leyendo las corridas del experimento…")
def load_launch(folder: str, stamp: float):
    # stamp (fecha de modificación) invalida la caché cuando el lanzamiento cambia
    return grid_analysis.load(folder)


def launch_stamp(folder: Path) -> float:
    summary = folder / "summary.csv"
    return summary.stat().st_mtime if summary.exists() else max(
        (p.stat().st_mtime for p in folder.glob("config*/*")), default=0.0)


def label(factor: str) -> str:
    return FACTOR_LABELS.get(factor, factor)


def levels_text(row, factors) -> str:
    return " · ".join(common.operator_label(row[f]) for f in factors)


# SBRP_RESULTS_DIR permite analizar resultados guardados en otra carpeta
results_dir = Path(os.environ.get("SBRP_RESULTS_DIR", common.RESULTS_DIR))
launches = sorted((p.parent for p in results_dir.rglob("grid.csv")), key=lambda p: p.name, reverse=True)
if not launches:
    st.info("No hay experimentos de rejilla en results/. Lánzalos con `python app/grid.py` (ver README) y copia aquí "
            "la carpeta del lanzamiento si se ejecutó en otra máquina.")
    st.stop()

# ------------------------- Selección -------------------------
with st.sidebar:
    st.header("Experimento")
    folder = st.selectbox("Lanzamiento", launches, format_func=lambda p: p.relative_to(results_dir).as_posix(),
                          help="Carpetas de results/ con grid.csv, de la más reciente a la más antigua.")
    try:
        runs, factors = load_launch(str(folder), launch_stamp(folder))
    except Exception as error:
        widgets.show_error("No se pudo leer el experimento", error)
        st.stop()
    if runs.empty:
        st.warning("El experimento aún no tiene corridas terminadas.")
        st.stop()

    st.subheader("Filtros")
    selected = {}
    for factor in factors:
        options = sorted(runs[factor].dropna().unique())
        selected[factor] = st.multiselect(label(factor), options, format_func=common.operator_label,
                                          placeholder="Todos", key=f"calibration-{factor}")
    instances = st.multiselect("Instancias", sorted(runs["instance"].unique(), key=common._natural_key),
                               placeholder="Todas", format_func=common.instance_name)
    top = st.slider("Combinaciones en el ranking", 5, 100, 20, step=5)

mask = pd.Series(True, index=runs.index)
for factor, values in selected.items():
    if values:
        mask &= runs[factor].isin(values)
if instances:
    mask &= runs["instance"].isin(instances)
data = runs[mask]
if data.empty:
    st.info("Ninguna corrida cumple los filtros.")
    st.stop()

table, friedman = grid_analysis.ranking(data, factors)
mean_ranks = table.set_index("config")["rango_medio"]
manifest_runs = None
try:
    manifest_runs = len(json.loads((folder / "manifest.json").read_text(encoding="utf-8"))["runs"])
except Exception:
    pass

# ------------------------- Resumen -------------------------
best = table.iloc[0]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Combinaciones", f"{data['config'].nunique()}",
          help="Combinaciones de operadores que cumplen los filtros.")
c2.metric("Corridas", f"{len(runs)}" + (f" / {manifest_runs}" if manifest_runs else ""),
          help="Corridas terminadas del experimento (de las previstas en el manifiesto).")
c3.metric("Bloques completos", f"{friedman['blocks']}",
          help="Pares (instancia, corrida) en los que terminaron todas las combinaciones filtradas. El ranking de "
               "Friedman solo usa estos bloques.")
c4.metric("Mejor gap medio", f"{best['gap_medio']:+.1%}", help="Gap medio de la combinación mejor clasificada.")
if manifest_runs and len(runs) < manifest_runs:
    st.warning(f"El experimento no ha terminado: {len(runs)} de {manifest_runs} corridas. Los resultados son parciales.")
st.markdown(f"**Mejor combinación:** {levels_text(best, factors)}")
if friedman["p_value"] is not None:
    verdict = "hay diferencias significativas" if friedman["p_value"] < ALPHA else "no hay diferencias significativas"
    tied = int((table["p_holm"].fillna(1) >= ALPHA).sum())
    st.caption(f"Prueba de Friedman sobre {friedman['blocks']} bloques: χ² = {friedman['statistic']:.1f}, "
               f"p = {friedman['p_value']:.2g}, así que {verdict} entre las combinaciones. Con la corrección de Holm, "
               f"{tied} combinaciones no se distinguen de la mejor (p ≥ {ALPHA}).")

tab_ranking, tab_factors, tab_interaction, tab_instances = st.tabs(
    ["Ranking", "Efecto de cada factor", "Interacciones", "Por instancia"])

# ------------------------- Ranking -------------------------
with tab_ranking:
    shown = table.head(top).copy()
    shown["≈ mejor"] = shown["p_holm"].isna() | (shown["p_holm"] >= ALPHA)
    for factor in factors:
        shown[factor] = shown[factor].map(common.operator_label)
    columns = ["posición", *factors, "gap_medio", "mejor_gap", "rango_medio", "p_holm", "≈ mejor", "tiempo_medio",
               "corridas", "config"]
    st.dataframe(shown[columns], hide_index=True, width="stretch", column_config={
        "posición": st.column_config.NumberColumn("#", width="small"),
        **{f: st.column_config.TextColumn(label(f)) for f in factors},
        "gap_medio": st.column_config.NumberColumn("Gap medio", format="percent",
                                                   help="Media del gap sobre el mejor conocido en todas sus corridas."),
        "mejor_gap": st.column_config.NumberColumn("Mejor gap", format="percent"),
        "rango_medio": st.column_config.NumberColumn("Rango medio", format="%.1f",
                                                     help="Posición media dentro de cada bloque (1 = la mejor)."),
        "p_holm": st.column_config.NumberColumn("p (Holm)", format="%.3f",
                                                help="p-valor ajustado de la comparación con la mejor combinación."),
        "≈ mejor": st.column_config.CheckboxColumn("≈ mejor", help=f"No se distingue de la mejor (p ≥ {ALPHA})."),
        "tiempo_medio": st.column_config.NumberColumn("Tiempo medio (s)", format="%.1f"),
        "corridas": st.column_config.NumberColumn("Corridas"),
        "config": st.column_config.TextColumn("Config"),
    })
    st.caption("El rango medio es la posición media de la combinación en cada bloque (misma instancia y semilla). "
               "Se usa en lugar del gap medio para el orden porque no lo dominan las instancias con gaps grandes.")
    st.download_button("Descargar ranking (CSV)", table.to_csv(index=False).encode("utf-8"), "ranking.csv", "text/csv")

# ------------------------- Efecto de cada factor -------------------------
with tab_factors:
    st.caption("Cada barra es el gap medio de todas las corridas que usan ese nivel, promediando sobre el resto de "
               "operadores. La tabla añade el gap medio de la mejor combinación con ese nivel: un nivel puede ser "
               "malo de media y aun así formar parte de la mejor combinación.")
    dark = widgets.is_dark()
    ink = common.INK[dark]
    for factor in factors:
        effects = grid_analysis.factor_effects(data, factor, mean_ranks)
        if len(effects) < 2:
            continue
        st.subheader(label(factor))
        left, right = st.columns([3, 2])
        names = [common.operator_label(level) for level in effects.index]
        fig = go.Figure(go.Bar(
            x=effects["gap_medio"], y=names, orientation="h", marker=dict(color=common.SERIES[0], cornerradius=4),
            text=[f"{v:+.1%}" for v in effects["gap_medio"]], textposition="outside",
            textfont=dict(color=ink[0]), cliponaxis=False,
            hovertemplate="%{y}<br>Gap medio: %{x:+.1%}<extra></extra>"))
        fig.update_layout(height=70 + 34 * len(effects), margin=dict(l=10, r=60, t=10, b=10), showlegend=False,
                          xaxis=dict(tickformat="+.0%", title="Gap medio sobre el mejor conocido",
                                     gridcolor="rgba(128,128,128,0.15)", zeroline=False),
                          yaxis=dict(autorange="reversed"), bargap=0.35)
        left.plotly_chart(fig, width="stretch", key=f"effect-{factor}")
        details = effects.reset_index().rename(columns={factor: "nivel"})
        details["nivel"] = details["nivel"].map(common.operator_label)
        right.dataframe(details, hide_index=True, width="stretch", column_config={
            "nivel": st.column_config.TextColumn(label(factor)),
            "gap_medio": st.column_config.NumberColumn("Gap medio", format="percent"),
            "mejor_combinación": st.column_config.NumberColumn("Mejor combinación", format="percent"),
            "rango_medio": st.column_config.NumberColumn("Rango medio", format="%.0f"),
            "tiempo_medio": st.column_config.NumberColumn("Tiempo (s)", format="%.1f"),
        })

# ------------------------- Interacciones -------------------------
with tab_interaction:
    default_rows = factors.index("crossover_operator") if "crossover_operator" in factors else 0
    default_columns = factors.index("mutation_operator") if "mutation_operator" in factors else min(1, len(factors) - 1)
    c1, c2 = st.columns(2)
    rows_factor = c1.selectbox("Filas", factors, index=default_rows, format_func=label)
    columns_factor = c2.selectbox("Columnas", factors, index=default_columns, format_func=label)
    if rows_factor == columns_factor:
        st.info("Elige dos factores distintos.")
    else:
        matrix = grid_analysis.interaction(data, rows_factor, columns_factor)
        matrix = matrix.loc[matrix.mean(axis=1).sort_values().index, matrix.mean(axis=0).sort_values().index]
        dark = widgets.is_dark()
        ramp = common.SEQUENTIAL_DARK if dark else common.SEQUENTIAL
        # Un solo tono: más intenso = gap mayor (peor)
        scale = [[0, "rgba(57,135,229,0.08)"], [0.5, ramp[0]], [1, ramp[2]]] if not dark else \
            [[0, "rgba(37,106,191,0.15)"], [0.5, ramp[1]], [1, ramp[2]]]
        values = matrix.values
        threshold = (pd.Series(values.ravel()).quantile(0.6)) if values.size else 0
        text_colors = common.INK[dark]
        fig = go.Figure(go.Heatmap(
            z=values, x=[common.operator_label(c) for c in matrix.columns],
            y=[common.operator_label(r) for r in matrix.index], colorscale=scale, xgap=2, ygap=2,
            colorbar=dict(title="Gap", tickformat="+.0%"),
            hovertemplate=f"{label(rows_factor)}: %{{y}}<br>{label(columns_factor)}: %{{x}}<br>"
                          "Gap medio: %{z:+.1%}<extra></extra>"))
        for i, row in enumerate(matrix.index):
            for j, column in enumerate(matrix.columns):
                value = values[i, j]
                if pd.notna(value):
                    light_cell = (value <= threshold) != dark
                    fig.add_annotation(x=common.operator_label(column), y=common.operator_label(row),
                                       text=f"{value:+.0%}", showarrow=False, font=dict(
                                           size=11, color=text_colors[0] if light_cell else text_colors[2]))
        fig.update_layout(height=120 + 42 * len(matrix.index), margin=dict(l=10, r=10, t=10, b=10),
                          yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, width="stretch")
        st.caption("Gap medio de las corridas con cada par de niveles; filas y columnas ordenadas de mejor a peor. "
                   "Si el orden de una fila cambia mucho de una columna a otra, los dos factores interactúan.")

# ------------------------- Por instancia -------------------------
with tab_instances:
    leaders = table.head(5)["config"].tolist()
    per_instance = data[data["config"].isin(leaders)].pivot_table(index="instance", columns="config", values="gap",
                                                                  aggfunc="mean")
    per_instance = per_instance.reindex(sorted(per_instance.index, key=common._natural_key))[leaders]
    best_per_instance = data.groupby("instance")["gap"].min().reindex(per_instance.index)
    per_instance.insert(0, "mejor corrida de la rejilla", best_per_instance)
    names = {c: f"#{i} {c}" for i, c in enumerate(leaders, 1)}
    per_instance.index = [common.instance_name(i) for i in per_instance.index]
    st.markdown("**Gap medio por instancia de las 5 mejores combinaciones**, y el mejor gap logrado por cualquier "
                "corrida de la rejilla en esa instancia")
    st.dataframe(per_instance.rename(columns=names).style.format("{:+.1%}", na_rep="—"), width="stretch")
    st.caption("Las combinaciones son las 5 primeras del ranking (ver su composición en la pestaña Ranking). "
               "Un gap de +0.0% iguala el mejor valor conocido; los óptimos probados están en "
               "data/instances/best_known.csv.")
