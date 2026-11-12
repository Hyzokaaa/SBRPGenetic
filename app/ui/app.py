"""
Punto de entrada de la interfaz: streamlit run app/ui/app.py
"""
import streamlit as st

st.set_page_config(page_title="SBRPGenetic", page_icon="🚌", layout="wide")

navigation = st.navigation([
    st.Page("views/home.py", title="Inicio", icon="🏠", default=True),
    st.Page("views/live_run.py", title="Ejecutar en vivo", icon="▶️"),
    st.Page("views/operator_lab.py", title="Laboratorio de operadores", icon="🧪"),
    st.Page("views/compare.py", title="Comparar configuraciones", icon="📊"),
    st.Page("views/results.py", title="Resultados guardados", icon="🗂️"),
])
navigation.run()
