"""Reporte de sismos en cubos 3D (México, Perú y Venezuela) con matplotlib.

Cada sismo se grafica como un punto en un cubo tridimensional:
    X = longitud, Y = latitud, Z = profundidad (km, invertida).

La selección por país es una caja delimitadora aproximada (bounding box),
no el contorno político exacto.

Instalación:
    py -m pip install -r requirements.txt

Ejecución (como reporte independiente):
    py -m streamlit run reporte_cubos_3d.py
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import pydeck as pdk
import streamlit as st
from pydeck.data_utils import compute_view
from streamlit.errors import StreamlitAPIException

from reporte_sismos import cargar_datos, listar_archivos_datos

# Cajas delimitadoras aproximadas: (lat_min, lat_max), (lon_min, lon_max).
PAISES = {
    "México": {"lat": (14.0, 33.0), "lon": (-119.0, -86.0)},
    "Perú": {"lat": (-19.0, 0.5), "lon": (-82.0, -68.0)},
    "Venezuela": {"lat": (0.6, 12.3), "lon": (-73.4, -59.7)},
}


def filtrar_pais(datos: pd.DataFrame, nombre_pais: str) -> pd.DataFrame:
    caja = PAISES[nombre_pais]
    return datos[datos["latitude"].between(*caja["lat"]) & datos["longitude"].between(*caja["lon"])]


def graficar_cubo(datos_pais: pd.DataFrame, nombre_pais: str) -> plt.Figure:
    fig = plt.figure(figsize=(5.5, 5.5))
    ax = fig.add_subplot(111, projection="3d")
    dispersion = ax.scatter(
        datos_pais["longitude"],
        datos_pais["latitude"],
        datos_pais["depth"],
        c=datos_pais["mag"],
        cmap="inferno",
        s=8 + datos_pais["mag"] ** 2.2,
        alpha=0.55,
        edgecolors="none",
    )
    ax.set_xlabel("Longitud")
    ax.set_ylabel("Latitud")
    ax.set_zlabel("Profundidad (km)")
    ax.set_title(f"Sismos en {nombre_pais}")
    ax.invert_zaxis()  # la superficie queda arriba; la profundidad crece hacia abajo
    ax.set_box_aspect((1, 1, 1))  # fuerza la forma de cubo, sin importar la escala de los datos
    fig.colorbar(dispersion, ax=ax, shrink=0.6, pad=0.1, label="Magnitud")
    return fig


def graficar_mapa(datos_pais: pd.DataFrame) -> pdk.Deck:
    """Ubica en un mapa los mismos puntos graficados en el cubo."""
    mapa = datos_pais.copy()
    mapa["radio"] = ((mapa["mag"].clip(lower=0) + 1) ** 2) * 3000
    capa = pdk.Layer(
        "ScatterplotLayer",
        data=mapa,
        get_position="[longitude, latitude]",
        get_radius="radio",
        get_fill_color="[220, 38, 38, 140]",
        pickable=True,
        stroked=True,
        get_line_color="[120, 20, 20, 200]",
        line_width_min_pixels=1,
    )
    vista = compute_view(mapa[["longitude", "latitude"]])
    return pdk.Deck(
        layers=[capa],
        initial_view_state=vista,
        tooltip={"text": "Magnitud: {mag}\nProfundidad: {depth} km\nLugar: {place}"},
    )


def main() -> None:
    try:
        st.set_page_config(page_title="Cubos 3D de sismos", page_icon="📦", layout="wide")
    except StreamlitAPIException:
        pass  # Ya fue configurada por inicio.py al usarse como subpágina.

    st.title("📦 Sismos en 3D: " + ", ".join(PAISES))
    st.caption(
        "Cada cubo grafica longitud (X), latitud (Y) y profundidad (Z, invertida) de los sismos "
        "dentro de una caja delimitadora aproximada del país."
    )

    archivos = listar_archivos_datos()
    if not archivos:
        st.error("No se encontraron archivos `terremotos_*.csv` en `data/`.")
        st.stop()

    datos = cargar_datos(tuple(str(archivo) for archivo in archivos))
    datos = datos.dropna(subset=["latitude", "longitude", "depth"])
    fecha_minima = datos["time"].dt.date.min()
    fecha_maxima = datos["time"].dt.date.max()

    with st.sidebar:
        st.header("Filtros")
        fechas = st.date_input(
            "Período", value=(fecha_minima, fecha_maxima), min_value=fecha_minima, max_value=fecha_maxima
        )
        magnitud_minima = st.slider("Magnitud mínima", 2.5, 8.0, 2.5, 0.1)
        maximo_puntos = st.slider("Máximo de puntos por país (muestra aleatoria)", 1000, 50000, 15000, 1000)

    if len(fechas) != 2:
        st.info("Selecciona una fecha de inicio y una de fin.")
        st.stop()

    inicio, fin = pd.Timestamp(fechas[0], tz="UTC"), pd.Timestamp(fechas[1], tz="UTC") + pd.Timedelta(days=1)
    datos_filtrados = datos[
        (datos["time"] >= inicio) & (datos["time"] < fin) & (datos["mag"] >= magnitud_minima)
    ]

    columnas = st.columns(len(PAISES))
    for columna, nombre_pais in zip(columnas, PAISES):
        datos_pais = filtrar_pais(datos_filtrados, nombre_pais)
        total = len(datos_pais)
        with columna:
            st.subheader(nombre_pais)
            if datos_pais.empty:
                st.warning("No hay sismos que cumplan los filtros elegidos.")
                continue
            if total > maximo_puntos:
                datos_pais = datos_pais.sample(maximo_puntos, random_state=42)
            st.pyplot(graficar_cubo(datos_pais, nombre_pais), use_container_width=True)
            texto = f"{total:,} sismos cumplen el filtro".replace(",", ".")
            if total > maximo_puntos:
                texto += f"; se muestra una muestra aleatoria de {maximo_puntos:,}.".replace(",", ".")
            else:
                texto += "."
            st.caption(texto)
            st.caption("Mismos puntos del cubo, ubicados en el mapa:")
            st.pydeck_chart(graficar_mapa(datos_pais))


if __name__ == "__main__":
    main()
