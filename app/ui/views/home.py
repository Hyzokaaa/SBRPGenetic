import streamlit as st

import common
import widgets


@st.cache_resource(show_spinner="Cargando instancia…")
def cached_problem(instance_label: str, assign_strategy: str):
    return common.load_problem(common.list_instances()[instance_label], assign_strategy)


st.title("SBRPGenetic")
st.caption("Laboratorio del algoritmo genético para el problema de ruteo de autobuses escolares (SBRP).")

PAGES = [
    ("views/live_run.py", "Ejecutar en vivo", "▶️",
     "Ejecuta el GA con cualquier configuración u operador y sigue la convergencia generación a generación."),
    ("views/operator_lab.py", "Laboratorio de operadores", "🧪",
     "Aplica un cruce o una mutación a dos padres y mira qué hereda el hijo y qué corrige la reparación."),
    ("views/compare.py", "Comparar configuraciones", "📊",
     "Ejecuta varias configuraciones con varias semillas en paralelo y compara sus distancias."),
    ("views/results.py", "Resultados guardados", "🗂️",
     "Explora los CSV que genera app/main.py y revalida corridas antiguas."),
]
for column, (page, title, icon, description) in zip(st.columns(len(PAGES)), PAGES):
    with column.container(border=True):
        st.page_link(page, label=title, icon=icon)
        st.caption(description)

st.subheader("Instancia")
col1, col2 = st.columns(2)
instance_label, _ = widgets.instance_select(col1)
assign_options = common.operator_names("stop_assign")
assign_strategy = col2.selectbox("Estrategia de asignación", assign_options,
                                 index=assign_options.index("H_STUDENT_TO_CLOSEST_STOP_STRATEGY"),
                                 format_func=common.operator_label,
                                 help="Cómo se asigna cada estudiante a una parada dentro de su distancia a pie.")

try:
    problem = cached_problem(instance_label, assign_strategy)
except Exception as error:
    st.error(f"No se pudo asignar a todos los estudiantes de {common.instance_name(instance_label)}: {error}. "
             "Algún estudiante no tiene ninguna parada dentro de su distancia a pie con esta estrategia: "
             "prueba otra estrategia de asignación u otra instancia.")
    st.stop()

summary = common.instance_summary(problem)
for column, (label, value) in zip(st.columns(len(summary)), summary.items()):
    column.metric(label, value, help=common.SUMMARY_HELP.get(label))

show_students = st.toggle("Mostrar estudiantes y su parada asignada", value=True)
st.plotly_chart(common.instance_figure(problem, show_students=show_students, show_assignment=show_students,
                                       dark=widgets.is_dark()),
                width="stretch",
                alt=f"Mapa de la instancia {common.instance_name(instance_label)}: escuela, paradas y estudiantes.")
st.caption("★ escuela · ● parada (tamaño según estudiantes asignados) · ○ parada sin estudiantes · "
           "punto pequeño gris: estudiante, unido a su parada. Pasa el ratón por encima para ver los identificadores.")
