import random
import time

import pandas as pd
import streamlit as st

import common
from src.algorithm.genetic_algorithm.genetic_algorithm_executor import GeneticAlgorithmExecutor
from src.analysis.metrics import population_stats

st.title("Ejecutar en vivo")

instances, configs = common.list_instances(), common.list_configs()

# ------------------------- Parámetros -------------------------
with st.sidebar:
    st.header("Ejecución")
    instance_label = st.selectbox("Instancia", list(instances),
                                  index=list(instances).index("real/inst54-7s20-100-c50-w20.xpress")
                                  if "real/inst54-7s20-100-c50-w20.xpress" in instances else 0)
    config_name = st.selectbox("Configuración", list(configs), index=len(configs) - 1)
    base = common.read_config(configs[config_name])

    def operator_select(label, key, family):
        options = common.operator_names(family)
        current = base[key]["name"] if isinstance(base.get(key), dict) else base.get(key)
        return st.selectbox(label, options, index=options.index(current) if current in options else 0,
                            format_func=common.operator_label, key=f"{config_name}-{key}")

    with st.expander("Operadores", expanded=True):
        stop_assign = operator_select("Asignación", "stop_assign_strategy", "stop_assign")
        route_generator = operator_select("Generación de rutas", "route_generator_strategy", "route_generator")
        selection = operator_select("Selección", "selection_operator", "selection")
        crossover = operator_select("Cruce", "crossover_operator", "crossover")
        mutation = operator_select("Mutación", "mutation_operator", "mutation")

    with st.expander("Parámetros", expanded=True):
        population_size = st.number_input("Población", 4, 5000, min(int(base["initial_population_size"]), 200), step=10,
                                          key=f"{config_name}-pop")
        max_iter = st.number_input("Máx. generaciones", 1, 5000, min(int(base["max_iter"]), 50), key=f"{config_name}-iter")
        max_stagnation = st.number_input("Parar tras N generaciones sin mejora", 1, 5000,
                                         int(base["max_stagnation_iter"]), key=f"{config_name}-stag")
        tournament_size = st.number_input("Tamaño de torneo", 2, 100, int(base["tournament_size"]), key=f"{config_name}-tour")
        crossover_rate = st.slider("Tasa de cruce", 0.0, 1.0, float(base["crossover_rate"]), key=f"{config_name}-cr")
        mutation_rate = st.slider("Tasa de mutación", 0.0, 1.0, float(base["mutation_rate"]), key=f"{config_name}-mr")
        elitism_size = st.number_input("Élite", 0, 50, int(base.get("elitism_size", 1)), key=f"{config_name}-elite")
        seed = st.number_input("Semilla", 0, 10 ** 6, 1)
        map_every = st.number_input("Actualizar el mapa cada N generaciones", 1, 100, 5)

    run = st.button("▶ Ejecutar", type="primary", width="stretch")

if population_size <= tournament_size:
    st.warning("La población debe ser mayor que el tamaño del torneo.")
    st.stop()

# ------------------------- Ejecución -------------------------
if run:
    random.seed(int(seed))
    config = common.build_config(configs[config_name], instances[instance_label], {
        "stop_assign_strategy": stop_assign, "route_generator_strategy": route_generator,
        "selection_operator": selection, "crossover_operator": crossover, "mutation_operator": mutation,
        "initial_population_size": int(population_size), "max_iter": int(max_iter),
        "max_stagnation_iter": int(max_stagnation), "tournament_size": int(tournament_size),
        "crossover_rate": float(crossover_rate), "mutation_rate": float(mutation_rate), "elitism_size": int(elitism_size),
    })

    progress = st.progress(0.0, text="Generando población inicial…")
    metrics_placeholder = st.empty()
    left, right = st.columns([3, 2])
    map_placeholder = left.empty()
    convergence_placeholder = right.empty()
    diversity_placeholder = right.empty()

    history = []
    last_best = {"value": None}
    start = time.time()

    def on_generation(generation, population, problem, stats):
        summary = population_stats(population, problem)
        children = max(1, len(population) - config.elitism_size)
        history.append({
            "generación": generation, "mejor": summary["best"], "media": summary["mean"], "peor": summary["worst"],
            "mejor_global": problem.objective_function(problem.best_solution) if problem.best_solution else None,
            "diversidad": summary["diversity"], "factibles": summary["feasible"],
            "cruces": stats.get("crossovers", 0), "mutaciones": stats.get("mutations", 0) / children,
            "mutaciones_duplicados": stats.get("duplicate_mutations", 0) / children,
        })
        df = pd.DataFrame(history)
        progress.progress(min(1.0, generation / config.max_iter),
                          text=f"Generación {generation}/{config.max_iter} · {time.time() - start:.0f} s")
        with metrics_placeholder.container():
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Mejor global", f"{history[-1]['mejor_global']:.1f}" if history[-1]["mejor_global"] else "—",
                      delta=(f"{history[-1]['mejor_global'] - history[0]['mejor_global']:.1f}"
                             if generation and history[0]["mejor_global"] else None), delta_color="inverse")
            c2.metric("Diversidad", f"{summary['diversity']:.0%}")
            c3.metric("Factibles", f"{summary['feasible']:.0%}")
            c4.metric("Generación", generation)
        convergence_placeholder.plotly_chart(common.convergence_figure(df), width="stretch", key=f"conv-{generation}")
        diversity_placeholder.plotly_chart(common.percentage_figure(df, "diversidad", "Diversidad de la población"),
                                           width="stretch", key=f"div-{generation}")
        best = history[-1]["mejor_global"]
        if problem.best_solution is not None and (best != last_best["value"] or generation % map_every == 0):
            last_best["value"] = best
            map_placeholder.plotly_chart(common.solution_figure(problem, problem.best_solution,
                                                                title=f"Mejor solución · generación {generation}"),
                                         width="stretch", key=f"map-{generation}")

    try:
        result = GeneticAlgorithmExecutor().execute(config, on_generation=on_generation)
    except Exception as error:
        st.exception(error)
        st.stop()
    progress.empty()
    st.session_state["live_run"] = {
        "problem": result[0], "fitness": result[1], "best_iteration": result[2], "time": result[3],
        "stop_reason": result[4], "stop_iteration": result[5], "history": pd.DataFrame(history),
        "label": f"{config_name} · {instance_label}",
    }
    st.rerun()

# ------------------------- Resultado -------------------------
run_data = st.session_state.get("live_run")
if run_data is None:
    st.info("Elige la instancia, la configuración y los operadores en la barra lateral y pulsa **Ejecutar**. "
            "Las configuraciones se cargan como punto de partida y puedes cambiar cualquier operador o parámetro.")
    st.stop()

problem, history = run_data["problem"], run_data["history"]
solution = problem.best_solution
st.subheader(f"Resultado · {run_data['label']}")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Mejor distancia", f"{run_data['fitness']:.2f}" if run_data["fitness"] is not None else "—")
c2.metric("Encontrada en la generación", run_data["best_iteration"])
c3.metric("Parada", f"{'estancamiento' if run_data['stop_reason'] == 'stagnation' else 'máx. generaciones'} "
                    f"({run_data['stop_iteration']})")
c4.metric("Tiempo", f"{run_data['time']:.1f} s")
c5.metric("Rutas", f"{len(solution.get_representation())}/{len(problem.vehicles)}" if solution else "—")

if solution is None:
    st.error("No se encontró ninguna solución factible.")
    st.stop()

violations = problem.violations(solution)
if violations:
    st.error("La mejor solución incumple restricciones: " + "; ".join(violations))
else:
    st.success("La mejor solución es factible.")

routes = common.routes_table(problem, solution)
left, right = st.columns([3, 2])
with right:
    highlight = st.selectbox("Resaltar ruta", [None] + routes["Ruta"].tolist(),
                             format_func=lambda r: "Ninguna" if r is None else f"Ruta {r}")
    st.dataframe(routes, hide_index=True, width="stretch",
                 column_config={"Ocupación": st.column_config.ProgressColumn("Ocupación", format="percent",
                                                                             min_value=0, max_value=1)})
left.plotly_chart(common.solution_figure(problem, solution, highlight_route=highlight, show_students=False),
                  width="stretch")
st.caption("Color de las rutas: azul más oscuro = ruta más llena (estudiantes / capacidad). La ruta resaltada en naranja.")

tab1, tab2, tab3 = st.tabs(["Convergencia", "Diversidad y mutaciones", "Datos por generación"])
tab1.plotly_chart(common.convergence_figure(history, height=360), width="stretch")
with tab2:
    c1, c2 = st.columns(2)
    c1.plotly_chart(common.percentage_figure(history, "diversidad", "Diversidad de la población"), width="stretch")
    c2.plotly_chart(common.percentage_figure(history, "mutaciones_duplicados", "Mutaciones extra por hijo para evitar duplicados",
                                                fixed_range=False),
                    width="stretch")
tab3.dataframe(history, hide_index=True, width="stretch")
tab3.download_button("Descargar CSV", history.to_csv(index=False).encode("utf-8"), "generaciones.csv", "text/csv")
