"""
Controles y utilidades de Streamlit compartidos por las páginas. Se mantienen fuera de common.py para que los
procesos de experiment.py no tengan que importar Streamlit.
"""
import traceback

import streamlit as st

import common

DEFAULT_INSTANCE = "real/inst54-7s20-100-c50-w20.xpress"
INSTANCE_KEY = "instance"
# Claves de controles que comparten todas las páginas
SHARED_KEYS = (INSTANCE_KEY,)


def keep_shared_state():
    """
    Conserva el valor de los controles compartidos al cambiar de página: Streamlit borra el estado de un widget
    que no se dibuja en la ejecución, así que se vuelve a asignar antes de ejecutar la página.
    """
    for key in SHARED_KEYS:
        if key in st.session_state:
            st.session_state[key] = st.session_state[key]


def instance_select(container=None):
    """Selector de instancia común a todas las páginas. Devuelve (etiqueta, ruta)."""
    container = container or st
    instances = common.list_instances()
    if st.session_state.get(INSTANCE_KEY) not in instances:
        st.session_state[INSTANCE_KEY] = DEFAULT_INSTANCE if DEFAULT_INSTANCE in instances else next(iter(instances))
    label = container.selectbox("Instancia", list(instances), key=INSTANCE_KEY, format_func=common.instance_name,
                                help=common.INSTANCE_HELP)
    return label, instances[label]


def is_dark() -> bool:
    """True si el visitante usa el tema oscuro (para ajustar la tinta de los mapas)."""
    try:
        return st.context.theme.type == "dark"
    except Exception:
        return False


def show_error(message: str, error: Exception):
    """Mensaje de error legible con el detalle técnico plegado."""
    st.error(f"{message}: {error}")
    with st.expander("Detalle técnico"):
        st.code("".join(traceback.format_exception(error)), language="text")
