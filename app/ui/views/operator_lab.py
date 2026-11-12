import random

import pandas as pd
import streamlit as st

import common
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

instances = common.list_instances()


# ------------------------- Población -------------------------
def generate_population(instance_label, assign_strategy, route_generator, size, seed):
    random.seed(seed)
    problem = common.load_problem(instances[instance_label], assign_strategy)
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
    instance_label = st.selectbox("Instancia", list(instances),
                                  index=list(instances).index("real/inst54-7s20-100-c50-w20.xpress")
                                  if "real/inst54-7s20-100-c50-w20.xpress" in instances else 0)
    assign_options = common.operator_names("stop_assign")
    assign_strategy = st.selectbox("Asignación", assign_options, format_func=common.operator_label,
                                   index=assign_options.index("H_STUDENT_TO_CLOSEST_STOP_STRATEGY"))
    route_options = common.operator_names("route_generator")
    route_generator = st.selectbox("Generación de rutas", route_options, format_func=common.operator_label,
                                   index=route_options.index("RANDOM_ROUTE_GENERATION_STRATEGY"))
    size = st.number_input("Tamaño", 2, 200, 20)
    seed = st.number_input("Semilla", 0, 10 ** 6, 1)
    if st.button("Generar población", type="primary", width="stretch"):
        try:
            st.session_state["lab"] = dict(zip(("problem", "population"), generate_population(
                instance_label, assign_strategy, route_generator, int(size), int(seed))))
            st.session_state["lab"]["label"] = instance_label
            st.session_state.pop("lab_crossover", None)
            st.session_state.pop("lab_mutation", None)
        except Exception as error:
            st.error(f"No se pudo generar la población: {error}")

lab = st.session_state.get("lab")
if lab is None:
    st.info("Genera una población en la barra lateral para empezar.")
    st.stop()

problem, population = lab["problem"], lab["population"]
cost = problem.objective_function

table = pd.DataFrame([{"Individuo": i, "Distancia": round(cost(s), 2), "Rutas": len(s.get_representation()),
                       "Factible": problem.is_feasible(s)} for i, s in enumerate(population)])
with st.expander(f"Población · {lab['label']} · {len(population)} individuos", expanded=False):
    st.dataframe(table, hide_index=True, width="stretch")

labels = {i: f"#{i} · {cost(s):.1f}" for i, s in enumerate(population)}
c1, c2 = st.columns(2)
index_a = c1.selectbox("Padre A", list(labels), format_func=labels.get, index=0)
index_b = c2.selectbox("Padre B", list(labels), format_func=labels.get, index=min(1, len(labels) - 1))
parent_a, parent_b = population[index_a], population[index_b]
if index_a == index_b:
    st.caption("A y B son el mismo individuo: es un autocruce. Un cruce que respete lo común debería devolver al mismo padre.")

c1.plotly_chart(common.solution_figure(problem, parent_a, title=f"Padre A · {cost(parent_a):.2f}", height=380),
                width="stretch", key=f"parent-a-{index_a}")
c2.plotly_chart(common.solution_figure(problem, parent_b, title=f"Padre B · {cost(parent_b):.2f}", height=380),
                width="stretch", key=f"parent-b-{index_b}")
st.caption("Color de las rutas: azul más oscuro = ruta más llena.")


def violations_text(solution):
    violations = problem.violations(solution)
    return "Factible" if not violations else "; ".join(violations)


tab_crossover, tab_mutation = st.tabs(["Cruce y reparación", "Mutación"])

# ------------------------- Cruce -------------------------
with tab_crossover:
    c1, c2, c3 = st.columns([3, 1, 1])
    crossover = c1.selectbox("Operador de cruce", common.operator_names("crossover"), format_func=common.operator_label,
                             index=common.operator_names("crossover").index("EAX_CROSSOVER_OPERATOR_SBRP"))
    crossover_seed = c2.number_input("Semilla del operador", 0, 10 ** 6, 1, key="cx-seed")
    c3.write("")
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
            st.exception(error)

    result = st.session_state.get("lab_crossover")
    if result and result["parents"] == (index_a, index_b):
        st.markdown(f"**{common.operator_label(result['operator'])}** sobre A = #{index_a} y B = #{index_b}")
        stage = st.radio("Hijos", ["Después de reparar", "Antes de reparar (salida del cruce)"], horizontal=True)
        children = result["repaired"] if stage.startswith("Después") else result["children"]

        rows = []
        columns = st.columns(2)
        for k, (child, own, other, own_name) in enumerate([(children[0], parent_a, parent_b, "A"),
                                                           (children[1], parent_b, parent_a, "B")]):
            origin = edge_origin(child, parent_a, parent_b)
            counts = pd.Series(origin.values()).value_counts()
            child_cost = cost(child)
            rows.append({
                "Hijo": k + 1, "Parte de": f"Padre {own_name}", "Distancia": round(child_cost, 2),
                "Δ vs su padre": f"{100 * (child_cost - cost(own)) / cost(own):+.1f}%",
                "Mejor que ambos padres": child_cost < min(cost(parent_a), cost(parent_b)) - 1e-9,
                "Hereda del otro padre": f"{inheritance(child, own, other):.0%}",
                "Aristas A / B / común / nuevas": f"{counts.get('A', 0)} / {counts.get('B', 0)} / "
                                                  f"{counts.get('AB', 0)} / {counts.get('nueva', 0)}",
                "Rutas": len(child.get_representation()),
                "Restricciones": violations_text(child),
            })
            columns[k].plotly_chart(common.edge_origin_figure(problem, child, origin,
                                                              title=f"Hijo {k + 1} · {child_cost:.2f}", height=400),
                                    width="stretch", key=f"child-{k}-{stage}")
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
        st.caption("Aristas: azul = del padre A · naranja = del padre B · gris = comunes a ambos · verde = nuevas. "
                   "«Hereda del otro padre» = fracción de las aristas exclusivas del otro padre que aparecen en el hijo. "
                   "Las restricciones antes de reparar muestran lo que el cruce rompe por sí solo.")

# ------------------------- Mutación -------------------------
with tab_mutation:
    c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
    mutation = c1.selectbox("Operador de mutación", common.operator_names("mutation"), format_func=common.operator_label,
                            index=common.operator_names("mutation").index("COMPOSITE_MUTATION_OPERATOR_SBRP"))
    times = c2.number_input("Aplicaciones", 1, 100, 1)
    mutation_seed = c3.number_input("Semilla del operador", 0, 10 ** 6, 1, key="mut-seed")
    c4.write("")
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
            st.exception(error)

    result = st.session_state.get("lab_mutation")
    if result and result["parent"] == index_a:
        mutated = result["solution"]
        kept = solution_edges(mutated) & solution_edges(parent_a)
        removed = solution_edges(parent_a) - solution_edges(mutated)
        origin = {edge: ("AB" if edge in kept else "nueva") for edge in solution_edges(mutated)}
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Distancia", f"{cost(mutated):.2f}", delta=f"{cost(mutated) - cost(parent_a):+.2f}", delta_color="inverse")
        c2.metric("Aristas nuevas", len(solution_edges(mutated) - kept))
        c3.metric("Aristas eliminadas", len(removed))
        c4.metric("Rutas", len(mutated.get_representation()))
        if problem.violations(mutated):
            st.error("La mutación rompió restricciones: " + violations_text(mutated))
        else:
            st.success("La solución mutada es factible.")
        left, right = st.columns([3, 2])
        left.plotly_chart(common.edge_origin_figure(problem, mutated, origin, height=420,
                                                    title=f"Padre A tras {common.operator_label(result['operator'])}",
                                                    labels={"AB": "Conservada", "nueva": "Nueva"}),
                          width="stretch", key="mutated")
        right.dataframe(result["steps"], hide_index=True, width="stretch")
        st.caption("Gris = arista que ya tenía el padre A · verde = arista nueva creada por la mutación.")
