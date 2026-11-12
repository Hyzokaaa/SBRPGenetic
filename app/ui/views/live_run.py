import random
import time

import pandas as pd
import streamlit as st

import common
import widgets
from src.algorithm.genetic_algorithm.genetic_algorithm_executor import GeneticAlgorithmExecutor
from src.analysis.metrics import population_stats

st.title("Ejecutar en vivo")

configs = common.list_configs()

# ------------------------- Parámetros -------------------------
with st.sidebar:
    st.header("Ejecución")
    instance_label, instance_path = widgets.instance_select()
    config_name = st.selectbox("Configuración", list(configs), index=len(configs) - 1,
                               help="Punto de partida: carga sus operadores y parámetros, que puedes cambiar abajo.")
    base = common.read_config(configs[config_name])
    algorithm = base.get("algorithm", "GA")
    is_ga = algorithm == "GA"
    if not is_ga:
        st.info(f"Algoritmo de referencia: **{common.ALGORITHM_LABELS[algorithm]}**. Usa el mismo presupuesto "
                "que el GA (población × generaciones evaluaciones) para comparar con él.")

    def operator_select(label, key, family):
        options = common.operator_names(family)
        current = base[key]["name"] if isinstance(base.get(key), dict) else base.get(key)
        return st.selectbox(label, options, index=options.index(current) if current in options else 0,
                            format_func=common.operator_label, key=f"{config_name}-{key}")

    with st.expander("Operadores", expanded=True):
        stop_assign = operator_select("Asignación", "stop_assign_strategy", "stop_assign")
        route_generator = operator_select("Generación de rutas", "route_generator_strategy", "route_generator")
        selection = operator_select("Selección", "selection_operator", "selection") if is_ga else None
        crossover = operator_select("Cruce", "crossover_operator", "crossover") if is_ga else None
        mutation = operator_select("Mutación", "mutation_operator", "mutation") if "mutation_operator" in base else None

    with st.expander("Parámetros", expanded=True):
        population_size = st.number_input(
            "Población", 4, 5000, min(int(base["initial_population_size"]), 100), step=10, key=f"{config_name}-pop",
            help=f"Individuos por generación. La configuración usa {base['initial_population_size']}; "
                 "aquí se limita a 100 por defecto para que la primera ejecución sea rápida.")
        max_iter = st.number_input(
            "Máx. generaciones", 1, 5000, min(int(base["max_iter"]), 50), key=f"{config_name}-iter",
            help=f"La configuración usa {base['max_iter']}; aquí se limita a 50 por defecto.")
        max_stagnation = st.number_input("Parar tras N generaciones sin mejora", 1, 5000,
                                         int(base["max_stagnation_iter"]), key=f"{config_name}-stag",
                                         help="Criterio de estancamiento: la ejecución termina si la mejor distancia "
                                              "no mejora durante N generaciones seguidas.")
        tournament_size = crossover_rate = mutation_rate = elitism_size = None
        if is_ga:
            tournament_size = st.number_input("Tamaño de torneo", 2, 100, int(base["tournament_size"]),
                                              key=f"{config_name}-tour",
                                              help="Individuos que compiten en cada selección por torneo. "
                                                   "Debe ser menor que la población.")
            crossover_rate = st.slider("Tasa de cruce", 0.0, 1.0, float(base["crossover_rate"]), key=f"{config_name}-cr",
                                       help="Probabilidad de cruzar cada pareja seleccionada; si no se cruza, "
                                            "los hijos son copias de los padres.")
            mutation_rate = st.slider("Tasa de mutación", 0.0, 1.0, float(base["mutation_rate"]), key=f"{config_name}-mr",
                                      help="Probabilidad de mutar cada hijo, haya habido cruce o no.")
            elitism_size = st.number_input("Élite", 0, 50, int(base.get("elitism_size", 1)), key=f"{config_name}-elite",
                                           help="Mejores soluciones distintas que pasan intactas a la siguiente generación.")
        seed = st.number_input("Semilla", 0, 10 ** 6, 1, help="Con la misma semilla y parámetros, la ejecución se repite igual.")
        map_every = st.number_input("Actualizar el mapa cada N generaciones", 1, 100, 5,
                                    help="El mapa también se actualiza siempre que mejora la mejor solución. "
                                         "Valores altos aceleran la ejecución.")

    problems = []
    if is_ga and population_size <= tournament_size:
        problems.append("La población debe ser mayor que el tamaño del torneo.")
    if is_ga and elitism_size >= population_size:
        problems.append("La élite debe ser menor que la población; si no, no se generan hijos.")
    run = st.button("▶ Ejecutar", type="primary", width="stretch", disabled=bool(problems))
    for problem_text in problems:
        st.error(problem_text)

def optional(convert, value):
    """Convierte el valor de un control, o None si el control no se muestra para este algoritmo."""
    return None if value is None else convert(value)


params = {
    "Instancia": common.instance_name(instance_label), "Configuración base": config_name,
    "Algoritmo": common.ALGORITHM_LABELS[algorithm],
    "Asignación": common.operator_label(stop_assign), "Generación de rutas": common.operator_label(route_generator),
    "Selección": optional(common.operator_label, selection), "Cruce": optional(common.operator_label, crossover),
    "Mutación": optional(common.operator_label, mutation), "Población": int(population_size),
    "Máx. generaciones": int(max_iter), "Parar tras N sin mejora": int(max_stagnation),
    "Tamaño de torneo": optional(int, tournament_size), "Tasa de cruce": optional(float, crossover_rate),
    "Tasa de mutación": optional(float, mutation_rate), "Élite": optional(int, elitism_size), "Semilla": int(seed),
}
params = {key: value for key, value in params.items() if value is not None}

# ------------------------- Reproducción de una corrida guardada -------------------------
replay = st.session_state.get("replay_request")
replay_now = False
if replay:
    with st.container(border=True):
        st.markdown(f"**Reproducir una corrida guardada** · {replay['label']} · semilla {replay['seed']}")
        st.caption("Se usan la copia de la configuración guardada con la corrida y su semilla, por lo que se repite "
                   "exactamente la misma evolución. Los controles de la barra lateral no se aplican.")
        b1, b2, _ = st.columns([1, 1, 3])
        replay_now = b1.button("▶ Reproducir en vivo", type="primary", width="stretch")
        if b2.button("Descartar", width="stretch"):
            st.session_state.pop("replay_request")
            st.rerun()

# ------------------------- Ejecución -------------------------
if run or replay_now:
    if replay_now:
        run_seed, run_label = int(replay["seed"]), replay["label"]
        run_params = {"Reproducción de": replay["label"], "Configuración": replay["config_path"], "Semilla": run_seed}
        build_run_config = lambda: common.build_config(replay["config_path"], replay["instance_path"], {})
    else:
        run_seed, run_label, run_params = int(seed), f"{config_name} · {common.instance_name(instance_label)}", params
        build_run_config = lambda: common.build_config(configs[config_name], instance_path, {
            "stop_assign_strategy": stop_assign, "route_generator_strategy": route_generator,
            "selection_operator": selection, "crossover_operator": crossover, "mutation_operator": mutation,
            "initial_population_size": int(population_size), "max_iter": int(max_iter),
            "max_stagnation_iter": int(max_stagnation), "tournament_size": optional(int, tournament_size),
            "crossover_rate": optional(float, crossover_rate), "mutation_rate": optional(float, mutation_rate),
            "elitism_size": optional(int, elitism_size),
        })
    random.seed(run_seed)
    progress = st.progress(0.0, text="Generando población inicial…")
    st.caption("Cambiar cualquier control durante la ejecución la interrumpe.")
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
        children = max(1, len(population) - (config.elitism_size or 0))
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
        best, first = history[-1]["mejor_global"], history[0]["mejor_global"]
        with metrics_placeholder.container():
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Mejor distancia", f"{best:.2f}" if best is not None else "—",
                      delta=f"{best - first:+.2f}" if generation and best is not None and first is not None else None,
                      delta_color="inverse", help="Mejor solución factible encontrada hasta ahora. "
                                                  "La variación es respecto a la población inicial.")
            c2.metric("Diversidad", f"{summary['diversity']:.0%}",
                      help="Fracción de individuos distintos en la población (100% = todos diferentes).")
            c3.metric("Factibles", f"{summary['feasible']:.0%}",
                      help="Fracción de la población que cumple todas las restricciones.")
            c4.metric("Generación", f"{generation}/{config.max_iter}")
        convergence_placeholder.plotly_chart(common.convergence_figure(df), width="stretch", key=f"conv-{generation}")
        diversity_placeholder.plotly_chart(common.percentage_figure(df, "diversidad", "Diversidad de la población"),
                                           width="stretch", key=f"div-{generation}")
        if problem.best_solution is not None and (best != last_best["value"] or generation % map_every == 0):
            last_best["value"] = best
            map_placeholder.plotly_chart(common.solution_figure(problem, problem.best_solution, dark=widgets.is_dark(),
                                                                title=f"Mejor solución · generación {generation}"),
                                         width="stretch", key=f"map-{generation}")

    try:
        config = build_run_config()
        result = GeneticAlgorithmExecutor().execute(config, on_generation=on_generation)
    except Exception as error:
        progress.empty()
        widgets.show_error("La ejecución falló", error)
        st.stop()
    progress.empty()
    st.session_state["live_run"] = {
        "problem": result[0], "fitness": result[1], "best_iteration": result[2], "time": result[3],
        "stop_reason": result[4], "stop_iteration": result[5], "history": pd.DataFrame(history),
        "label": run_label, "params": run_params, "max_stagnation": int(config.max_stagnation_iter),
        "algorithm": config.algorithm,
        "replay_of": replay if replay_now else None,
    }
    if replay_now:
        st.session_state.pop("replay_request", None)
    st.rerun()

# ------------------------- Resultado -------------------------
run_data = st.session_state.get("live_run")
if run_data is None:
    st.info("Elige la instancia, la configuración y los operadores en la barra lateral y pulsa **Ejecutar**. "
            "La configuración es solo un punto de partida: puedes cambiar cualquier operador o parámetro. "
            "Con los valores por defecto la ejecución tarda unos segundos.")
    st.stop()

problem, history = run_data["problem"], run_data["history"]
solution = problem.best_solution
st.subheader(f"Resultado · {run_data['label']}")
replayed = run_data.get("replay_of")
if replayed:
    original, reproduced = replayed.get("original"), run_data["fitness"]
    if original is not None and reproduced is not None and abs(original - reproduced) < 1e-9:
        st.success(f"Reproducción exacta: la distancia coincide con la de la corrida original ({original:.2f}).")
    else:
        st.warning(f"La distancia reproducida ({reproduced if reproduced is None else f'{reproduced:.2f}'}) no coincide "
                   f"con la original ({original}). Puede deberse a cambios en el código desde que se ejecutó.")
elif run_data.get("params") != params:
    st.info("Los controles de la barra lateral cambiaron desde esta ejecución: este resultado corresponde a los "
            "parámetros de «Parámetros usados». Pulsa **Ejecutar** para aplicar los nuevos.")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Mejor distancia", f"{run_data['fitness']:.2f}" if run_data["fitness"] is not None else "—",
          help="Distancia total recorrida por todas las rutas de la mejor solución factible.")
c2.metric("Encontrada en la generación", run_data["best_iteration"])
stop_reason = common.STOP_REASONS.get(run_data["stop_reason"], run_data["stop_reason"])
c3.metric("Generaciones ejecutadas", run_data["stop_iteration"], help=f"Se detuvo por {stop_reason}.")
c4.metric("Tiempo", f"{run_data['time']:.1f} s")
c5.metric("Rutas / buses", f"{len(solution.get_representation())}/{len(problem.vehicles)}" if solution else "—",
          help="Rutas de la mejor solución frente a buses disponibles.")
if run_data["stop_reason"] == "stagnation":
    st.caption(f"Se detuvo por estancamiento: {run_data.get('max_stagnation', '')} generaciones seguidas sin mejorar.")
else:
    st.caption("Se detuvo al llegar al límite de generaciones: aumentarlo puede seguir mejorando la solución.")

with st.expander("Parámetros usados"):
    st.dataframe(pd.DataFrame({"Parámetro": list(run_data.get("params", {})),
                               "Valor": [str(v) for v in run_data.get("params", {}).values()]}),
                 hide_index=True, width="stretch")

if solution is None:
    st.error("No se encontró ninguna solución factible. Prueba con más población o generaciones, u otra generación de rutas.")
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
                                                                             min_value=0, max_value=1),
                                "Distancia": st.column_config.NumberColumn("Distancia", format="%.2f")})
left.plotly_chart(common.solution_figure(problem, solution, highlight_route=highlight, show_students=False,
                                         dark=widgets.is_dark()),
                  width="stretch", alt=f"Mapa de las {len(routes)} rutas de la mejor solución.")
st.caption("Cada ruta sale de la escuela (★) y regresa a ella; su color indica la ocupación del bus "
           "(ver la escala). La ruta resaltada se dibuja en naranja y el resto se atenúa.")

# Las mutaciones por hijo solo tienen sentido en el GA; las referencias evalúan bloques de soluciones
is_ga_run = run_data.get("algorithm", "GA") == "GA"
tab1, tab2, tab3, tab4 = st.tabs(["Convergencia", "Población" if is_ga_run else "Soluciones evaluadas",
                                  "Mutaciones", "Datos por generación"])
with tab1:
    st.plotly_chart(common.convergence_figure(history, height=360), width="stretch")
    st.caption("«Mejor de la población» es la mejor distancia factible de cada generación; «Media de las factibles», "
               "la media de las soluciones factibles. Si las dos curvas se juntan, la población ha convergido.")
with tab2:
    c1, c2 = st.columns(2)
    c1.plotly_chart(common.percentage_figure(history, "diversidad", "Diversidad de la población"), width="stretch")
    c2.plotly_chart(common.percentage_figure(history, "factibles", "Soluciones factibles"), width="stretch")
    st.caption("Diversidad = fracción de individuos distintos. Una caída rápida indica convergencia prematura.")
with tab3:
    if is_ga_run:
        st.plotly_chart(common.rate_figure(history, {"mutaciones": "Por la tasa de mutación",
                                                     "mutaciones_duplicados": "Extra para evitar duplicados"},
                                           "Mutaciones por hijo", "Mutaciones por hijo"), width="stretch")
        st.caption("Si las mutaciones extra crecen, el cruce está produciendo muchos hijos idénticos a otros ya "
                   "aceptados.")
    else:
        st.info("Esta vista solo aplica al algoritmo genético.")
with tab4:
    st.dataframe(history, hide_index=True, width="stretch", column_config={
        "mejor": st.column_config.NumberColumn(format="%.2f"), "media": st.column_config.NumberColumn(format="%.2f"),
        "peor": st.column_config.NumberColumn(format="%.2f"),
        "mejor_global": st.column_config.NumberColumn("mejor global", format="%.2f"),
        "diversidad": st.column_config.NumberColumn(format="percent"),
        "factibles": st.column_config.NumberColumn(format="percent"),
        "mutaciones": st.column_config.NumberColumn("mutaciones por hijo", format="%.2f"),
        "mutaciones_duplicados": st.column_config.NumberColumn("mutaciones extra por hijo", format="%.2f"),
    })
    st.download_button("Descargar CSV", history.to_csv(index=False).encode("utf-8"), "generaciones.csv", "text/csv")
