import random

import pandas as pd
import streamlit as st

import common
import widgets
from src.analysis.metrics import edge_origin, inheritance, solution_edges
from src.operators.crossover.crossover_parameters import CrossoverParameters
from src.operators.distance.distance_euclidean import EuclideanDistance
from src.operators.initial_construction.initial_construction_parameters import InitialConstructionParameters
from src.operators.mutation.mutation_parameters import MutationParameters
from src.operators.repair.repair_parameters import RepairParameters
from src.problems.problem_sbrp.operators.initial_solution.initial_solution_conform_operator_sbrp import \
    InitialSolutionOperatorSBRP

st.title("Laboratorio de operadores")
st.caption("Genera una población, elige dos padres y observa qué hace cada operador: qué hereda el hijo de cada padre, "
           "cuánto cambia el coste y qué corrige la reparación.")

dark = widgets.is_dark()


# ------------------------- Población -------------------------
def generate_population(instance_path, assign_strategy, route_generator, size, seed):
    random.seed(seed)
    problem = common.load_problem(instance_path, assign_strategy)
    parameters = InitialConstructionParameters(problem=problem, distance_operator=EuclideanDistance(),
                                               route_generator_strategy=common.instantiate(route_generator))
    repair = common.instantiate("REPAIR_OPERATOR_SBRP")
    population = []
    for _ in range(size):
        solution = InitialSolutionOperatorSBRP().generate(parameters)
        if problem.violations(solution):
            solution = repair.repair(RepairParameters(problem=problem, solutions=[solution], parents=[solution]))[0]
        population.append(solution)
    return problem, population


with st.sidebar:
    st.header("Población")
    instance_label, instance_path = widgets.instance_select()
    assign_options = common.operator_names("stop_assign")
    assign_strategy = st.selectbox("Asignación", assign_options, format_func=common.operator_label,
                                   index=assign_options.index("H_STUDENT_TO_CLOSEST_STOP_STRATEGY"))
    route_options = common.operator_names("route_generator")
    route_generator = st.selectbox("Generación de rutas", route_options, format_func=common.operator_label,
                                   index=route_options.index("RANDOM_ROUTE_GENERATION_STRATEGY"))
    size = st.number_input("Tamaño de la población", 2, 200, 20,
                           help="Individuos iniciales entre los que elegir los padres (ya reparados si eran infactibles).")
    seed = st.number_input("Semilla", 0, 10 ** 6, 1, help="Con la misma semilla se genera la misma población.")
    generate = st.button("Generar población", type="primary", width="stretch")

if generate:
    try:
        with st.spinner("Generando población…"):
            st.session_state["lab"] = dict(zip(("problem", "population"), generate_population(
                instance_path, assign_strategy, route_generator, int(size), int(seed))))
        st.session_state["lab"]["label"] = instance_label
        st.session_state.pop("lab_crossover", None)
        st.session_state.pop("lab_mutation", None)
    except Exception as error:
        st.session_state.pop("lab", None)
        widgets.show_error("No se pudo generar la población", error)

lab = st.session_state.get("lab")
if lab is None:
    st.info("Elige la instancia en la barra lateral y pulsa **Generar población** para empezar. "
            "Después podrás elegir dos padres y aplicarles un cruce o una mutación.")
    st.stop()
if lab["label"] != instance_label:
    st.warning(f"La población es de {common.instance_name(lab['label'])}. "
               f"Pulsa **Generar población** para usar {common.instance_name(instance_label)}.")

problem, population = lab["problem"], lab["population"]
cost = problem.objective_function

table = pd.DataFrame([{"Individuo": i, "Distancia": cost(s), "Rutas": len(s.get_representation()),
                       "Factible": problem.is_feasible(s)} for i, s in enumerate(population)])
with st.expander(f"Población · {common.instance_name(lab['label'])} · {len(population)} individuos", expanded=False):
    st.dataframe(table, hide_index=True, width="stretch",
                 column_config={"Distancia": st.column_config.NumberColumn(format="%.2f")})

labels = {i: f"#{i} · {cost(s):.2f}" for i, s in enumerate(population)}
c1, c2 = st.columns(2)
index_a = c1.selectbox("Padre A", list(labels), format_func=labels.get, index=0,
                       help="Individuo · distancia total. La mutación se aplica a este padre.")
index_b = c2.selectbox("Padre B", list(labels), format_func=labels.get, index=min(1, len(labels) - 1),
                       help="Individuo · distancia total.")
parent_a, parent_b = population[index_a], population[index_b]
if index_a == index_b:
    st.caption("A y B son el mismo individuo: es un autocruce. Un cruce que respete lo común debería devolver al mismo padre.")

c1.plotly_chart(common.solution_figure(problem, parent_a, title=f"Padre A · {cost(parent_a):.2f}", height=380, dark=dark),
                width="stretch", key=f"parent-a-{index_a}", alt="Rutas del padre A coloreadas por ocupación.")
c2.plotly_chart(common.solution_figure(problem, parent_b, title=f"Padre B · {cost(parent_b):.2f}", height=380, dark=dark),
                width="stretch", key=f"parent-b-{index_b}", alt="Rutas del padre B coloreadas por ocupación.")
st.caption("Color de las rutas: azul más oscuro = ruta más llena (ver la escala).")


def violations_text(solution):
    violations = problem.violations(solution)
    return "Factible" if not violations else "; ".join(violations)


tab_crossover, tab_mutation = st.tabs(["Cruce y reparación", "Mutación"])

# ------------------------- Cruce -------------------------
with tab_crossover:
    c1, c2, c3 = st.columns([3, 1, 1], vertical_alignment="bottom")
    crossover = c1.selectbox("Operador de cruce", common.operator_names("crossover"), format_func=common.operator_label,
                             index=common.operator_names("crossover").index("EAX_CROSSOVER_OPERATOR_SBRP"))
    crossover_seed = c2.number_input("Semilla del operador", 0, 10 ** 6, 1, key="cx-seed",
                                     help="Fija el azar del operador para repetir el mismo resultado.")
    if c3.button("Aplicar cruce", type="primary", width="stretch"):
        random.seed(int(crossover_seed))
        try:
            children = common.instantiate(crossover).crossover(
                CrossoverParameters(problem=problem, parent1=parent_a, parent2=parent_b))
            repaired = common.instantiate("REPAIR_OPERATOR_SBRP").repair(
                RepairParameters(problem=problem, solutions=list(children), parents=[parent_a, parent_b]))
            st.session_state["lab_crossover"] = {"operator": crossover, "parents": (index_a, index_b),
                                                 "children": children, "repaired": repaired}
        except Exception as error:
            widgets.show_error("El cruce falló", error)

    result = st.session_state.get("lab_crossover")
    if result is None:
        st.caption("Elige un operador y pulsa **Aplicar cruce**: verás los dos hijos antes y después de la reparación.")
    elif result["parents"] != (index_a, index_b):
        st.caption(f"El último cruce se aplicó a A = #{result['parents'][0]} y B = #{result['parents'][1]}. "
                   "Pulsa **Aplicar cruce** para cruzar los padres elegidos.")
    else:
        st.markdown(f"**{common.operator_label(result['operator'])}** sobre A = #{index_a} y B = #{index_b}")
        stage = st.radio("Hijos", ["Después de reparar", "Antes de reparar (salida del cruce)"], horizontal=True,
                         help="Antes de reparar se ve lo que el cruce rompe por sí solo.")
        children = result["repaired"] if stage.startswith("Después") else result["children"]

        rows = []
        columns = st.columns(2)
        for k, (child, own, other, own_name) in enumerate([(children[0], parent_a, parent_b, "A"),
                                                           (children[1], parent_b, parent_a, "B")]):
            origin = edge_origin(child, parent_a, parent_b)
            counts = pd.Series(origin.values()).value_counts()
            child_cost = cost(child)
            rows.append({
                "Hijo": k + 1, "Parte de": f"Padre {own_name}", "Distancia": child_cost,
                "Δ vs su padre": (child_cost - cost(own)) / cost(own),
                "Mejor que ambos padres": child_cost < min(cost(parent_a), cost(parent_b)) - 1e-9,
                "Hereda del otro padre": inheritance(child, own, other),
                "Aristas A / B / común / nuevas": f"{counts.get('A', 0)} / {counts.get('B', 0)} / "
                                                  f"{counts.get('AB', 0)} / {counts.get('nueva', 0)}",
                "Rutas": len(child.get_representation()),
                "Restricciones": violations_text(child),
            })
            columns[k].plotly_chart(common.edge_origin_figure(problem, child, origin, height=400, dark=dark,
                                                              title=f"Hijo {k + 1} (parte de {own_name}) · {child_cost:.2f}"),
                                    width="stretch", key=f"child-{k}-{stage}",
                                    alt=f"Aristas del hijo {k + 1} según el padre del que proceden.")
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", column_config={
            "Distancia": st.column_config.NumberColumn(format="%.2f"),
            "Δ vs su padre": st.column_config.NumberColumn(
                format="percent", help="Cambio relativo de distancia frente al padre del que parte (negativo = mejor)."),
            "Hereda del otro padre": st.column_config.NumberColumn(
                format="percent", help="Fracción de las aristas exclusivas del otro padre que aparecen en el hijo."),
            "Aristas A / B / común / nuevas": st.column_config.TextColumn(
                help="Aristas del hijo que vienen solo de A, solo de B, de ambos padres, o que no tenía ninguno."),
        })
        st.caption("Aristas: azul continua = del padre A · naranja discontinua = del padre B · gris = comunes a ambos · "
                   "verde punteada = nuevas.")

# ------------------------- Mutación -------------------------
with tab_mutation:
    c1, c2, c3, c4 = st.columns([3, 1, 1, 1], vertical_alignment="bottom")
    mutation = c1.selectbox("Operador de mutación", common.operator_names("mutation"), format_func=common.operator_label,
                            index=common.operator_names("mutation").index("COMPOSITE_MUTATION_OPERATOR_SBRP"))
    times = c2.number_input("Aplicaciones", 1, 100, 1, help="Veces seguidas que se aplica la mutación.")
    mutation_seed = c3.number_input("Semilla del operador", 0, 10 ** 6, 1, key="mut-seed",
                                    help="Fija el azar del operador para repetir el mismo resultado.")
    if c4.button("Mutar padre A", type="primary", width="stretch"):
        random.seed(int(mutation_seed))
        try:
            mutated = parent_a.copy()
            operator = common.instantiate(mutation)
            steps = []
            for step in range(int(times)):
                operator.mutate(MutationParameters(problem=problem, solution=mutated, distance_operator=EuclideanDistance()))
                steps.append({"Aplicación": step + 1, "Distancia": round(cost(mutated), 2),
                              "Restricciones": violations_text(mutated)})
            st.session_state["lab_mutation"] = {"operator": mutation, "parent": index_a, "solution": mutated,
                                                "steps": pd.DataFrame(steps)}
        except Exception as error:
            widgets.show_error("La mutación falló", error)

    result = st.session_state.get("lab_mutation")
    if result is None:
        st.caption("Elige un operador y pulsa **Mutar padre A**: verás qué aristas conserva y cuáles crea la mutación.")
    elif result["parent"] != index_a:
        st.caption(f"La última mutación se aplicó al individuo #{result['parent']}. "
                   "Pulsa **Mutar padre A** para mutar el padre elegido.")
    else:
        mutated = result["solution"]
        kept = solution_edges(mutated) & solution_edges(parent_a)
        removed = solution_edges(parent_a) - solution_edges(mutated)
        origin = {edge: ("AB" if edge in kept else "nueva") for edge in solution_edges(mutated)}
        st.markdown(f"**{common.operator_label(result['operator'])}** sobre A = #{index_a}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Distancia", f"{cost(mutated):.2f}", delta=f"{cost(mutated) - cost(parent_a):+.2f}", delta_color="inverse",
                  help="Distancia tras la mutación; la variación es respecto al padre A (negativa = mejor).")
        c2.metric("Aristas nuevas", len(solution_edges(mutated) - kept))
        c3.metric("Aristas eliminadas", len(removed))
        c4.metric("Rutas", len(mutated.get_representation()))
        if problem.violations(mutated):
            st.error("La mutación rompió restricciones: " + violations_text(mutated))
        else:
            st.success("La solución mutada es factible.")
        left, right = st.columns([3, 2])
        left.plotly_chart(common.edge_origin_figure(problem, mutated, origin, height=420, dark=dark,
                                                    title=f"Padre A tras {common.operator_label(result['operator'])}",
                                                    labels={"AB": "Conservada", "nueva": "Nueva"}),
                          width="stretch", key="mutated", alt="Aristas del padre A mutado: conservadas y nuevas.")
        right.dataframe(result["steps"], hide_index=True, width="stretch")
        st.caption("Gris continua = arista que ya tenía el padre A · verde punteada = arista nueva creada por la mutación.")
