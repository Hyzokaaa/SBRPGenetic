import streamlit as st

import common



@st.cache_resource(show_spinner="Cargando instancia…")
def cached_problem(instance_label: str, assign_strategy: str):
    return common.load_problem(common.list_instances()[instance_label], assign_strategy)


st.title("SBRPGenetic")
st.caption("Laboratorio del algoritmo genético para el problema de ruteo de autobuses escolares (SBRP).")

st.markdown(
    "Usa las páginas de la barra lateral para **ejecutar el GA en vivo**, probar los **operadores** "
    "sobre dos padres, **comparar configuraciones** o explorar los **resultados guardados**. "
    "Aquí puedes ver una instancia y la asignación de estudiantes a paradas."
)

instances = common.list_instances()
col1, col2 = st.columns([2, 2])
instance_label = col1.selectbox("Instancia", list(instances), index=list(instances).index("real/inst54-7s20-100-c50-w20.xpress")
                                if "real/inst54-7s20-100-c50-w20.xpress" in instances else 0)
assign_options = common.operator_names("stop_assign")
assign_strategy = col2.selectbox("Estrategia de asignación", assign_options,
                                 index=assign_options.index("H_STUDENT_TO_CLOSEST_STOP_STRATEGY"),
                                 format_func=common.operator_label)

try:
    problem = cached_problem(instance_label, assign_strategy)
except Exception as error:
    st.error(f"No se pudo asignar a todos los estudiantes: {error}")
    st.stop()

summary = common.instance_summary(problem)
for column, (label, value) in zip(st.columns(len(summary)), summary.items()):
    column.metric(label, value)

show_students = st.toggle("Mostrar estudiantes y su parada asignada", value=True)
st.plotly_chart(common.instance_figure(problem, show_students=show_students, show_assignment=show_students),
                width="stretch")
st.caption("★ escuela · ● parada (tamaño según estudiantes asignados) · ○ parada sin estudiantes · · estudiante")
