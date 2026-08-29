"""Punto de entrada de la app multipágina de sismos: índice + reportes 1 y 2.

Instalación:
    py -m pip install -r requirements.txt

Ejecución:
    py -m streamlit run inicio.py
"""

from __future__ import annotations

import streamlit as st


def mostrar_inicio() -> None:
    st.title("🌎 Reportes de terremotos")
    st.write("Elige un reporte en el menú lateral o desde los accesos directos de abajo.")
    st.page_link("reporte_sismos.py", label="Reporte 1: Resumen y mapa global", icon="🌍")
    st.page_link("reporte_cubos_3d.py", label="Reporte 2: Cubos 3D (México, Perú y Venezuela)", icon="📦")


pagina_inicio = st.Page(mostrar_inicio, title="Inicio", icon="🏠", default=True)
pagina_reporte_1 = st.Page("reporte_sismos.py", title="Reporte 1: Resumen y mapa", icon="🌍")
pagina_reporte_2 = st.Page("reporte_cubos_3d.py", title="Reporte 2: Cubos 3D", icon="📦")

navegacion = st.navigation([pagina_inicio, pagina_reporte_1, pagina_reporte_2])
st.set_page_config(page_title="Reportes de terremotos", page_icon="🌎", layout="wide")
navegacion.run()
