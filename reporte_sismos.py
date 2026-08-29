"""Reporte interactivo de sismos.

Instalación:
    py -m pip install streamlit pandas

Ejecución:
    py -m streamlit run reporte_sismos.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pydeck as pdk
import streamlit as st
from streamlit.errors import StreamlitAPIException


CARPETA_DATOS = Path("data")
PATRON_DATOS = "terremotos_*.csv"


def listar_archivos_datos() -> list[Path]:
    return sorted(CARPETA_DATOS.glob(PATRON_DATOS))


@st.cache_data(show_spinner="Cargando datos de terremotos...")
def cargar_datos(rutas: tuple[str, ...]) -> pd.DataFrame:
    datos = pd.concat((pd.read_csv(ruta) for ruta in rutas), ignore_index=True)
    datos["time"] = pd.to_datetime(datos["time"], errors="coerce", utc=True)
    datos["mag"] = pd.to_numeric(datos["mag"], errors="coerce")
    datos["latitude"] = pd.to_numeric(datos["latitude"], errors="coerce")
    datos["longitude"] = pd.to_numeric(datos["longitude"], errors="coerce")
    return datos.dropna(subset=["time", "mag"]).copy()


def etiqueta_rango(magnitud: float) -> str:
    # Los cortes son 2,5; 3,5; 4,5..., por lo que 3,4 sigue en 2,5–3,5.
    inicio = int((magnitud - 2.5) // 1) + 2.5
    return f"{inicio:.1f} - {inicio + 1:.1f}".replace(".", ",")


def clasificar_hemisferio(valor: float, positivo: str, negativo: str, cero: str) -> str:
    if pd.isna(valor):
        return "Sin coordenada"
    if valor > 0:
        return positivo
    if valor < 0:
        return negativo
    return cero


def mostrar_resumen(datos: pd.DataFrame) -> None:
    """Muestra los gráficos del panel principal dentro de su pestaña."""
    c1, c2, c3 = st.columns(3)
    c1.metric("Terremotos", f"{len(datos):,}".replace(",", "."))
    c2.metric("Magnitud máxima", f"{datos['mag'].max():.1f}")
    c3.metric("Años con registros", datos["año"].nunique())

    st.header("Cantidad de sismos por año")
    st.line_chart(datos.groupby("año").size().rename("Cantidad"))

    st.header("Cantidad por año y rango de magnitud")
    por_anio = pd.crosstab(datos["año"], datos["rango de magnitud"])
    orden = sorted(por_anio.columns, key=lambda rango: float(rango.split(",")[0]))
    st.bar_chart(por_anio[orden])

    st.header("Patrones temporales")
    por_hora = datos.groupby("hora").size().reindex(range(24), fill_value=0).rename("Cantidad")
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    por_dia = datos.groupby("día de semana").size().reindex(dias, fill_value=0).rename("Cantidad")
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    por_mes = datos.groupby("mes").size().reindex(meses, fill_value=0).rename("Cantidad")
    hora, dia, mes = st.columns(3)
    hora.bar_chart(por_hora)
    dia.bar_chart(por_dia)
    mes.bar_chart(por_mes)

    st.header("Distribución por hemisferio")
    izquierda, derecha = st.columns(2)
    izquierda.bar_chart(datos.groupby("hemisferio norte/sur").size().rename("Cantidad"))
    derecha.bar_chart(datos.groupby("hemisferio este/oeste").size().rename("Cantidad"))

    st.header("Top 10 sismos de mayor magnitud")
    columnas = ["time", "año", "mag", "latitude", "longitude", "place"]
    top_10 = datos.nlargest(10, "mag")[[c for c in columnas if c in datos.columns]].rename(columns={
        "time": "Fecha y hora (UTC)", "año": "Año", "mag": "Magnitud",
        "latitude": "Latitud", "longitude": "Longitud", "place": "Lugar",
    })
    st.dataframe(top_10, hide_index=True, use_container_width=True)


def mostrar_mapa(datos: pd.DataFrame) -> None:
    """Muestra los eventos filtrados sobre un mapa mundial."""
    st.header("Mapa de sismos")
    mapa = datos.dropna(subset=["latitude", "longitude"]).copy()
    if mapa.empty:
        st.warning("No hay coordenadas disponibles para los filtros elegidos.")
        return

    modo = st.radio(
        "Visualización",
        ["Puntos por magnitud", "Puntos de tamaño uniforme", "Mapa de calor"],
        horizontal=True,
    )
    escala = st.slider("Escala del tamaño de los puntos", min_value=0.25, max_value=3.0, value=1.0, step=0.25)

    if modo == "Mapa de calor":
        ponderar = st.checkbox("Ponderar el calor según la magnitud", value=True)
        capa = pdk.Layer(
            "HeatmapLayer",
            data=mapa,
            get_position="[longitude, latitude]",
            get_weight="mag" if ponderar else 1,
            radius_pixels=45,
            intensity=1.0,
            threshold=0.05,
            pickable=True,
        )
        descripcion = "El color muestra la concentración de sismos"
        if ponderar:
            descripcion += " ponderada por magnitud"
        descripcion += "."
    else:
        if modo == "Puntos por magnitud":
            mapa["radio"] = ((mapa["mag"].clip(lower=0) + 1) ** 2) * 4500 * escala
            descripcion = "El tamaño de cada punto es proporcional a su magnitud."
        else:
            mapa["radio"] = 16000 * escala
            descripcion = "Todos los puntos tienen el mismo tamaño."
        capa = pdk.Layer(
            "ScatterplotLayer",
            data=mapa,
            get_position="[longitude, latitude]",
            get_radius="radio",
            get_fill_color="[220, 38, 38, 155]",
            pickable=True,
            stroked=True,
            get_line_color="[120, 20, 20, 200]",
            line_width_min_pixels=1,
        )

    vista = pdk.ViewState(latitude=float(mapa["latitude"].mean()), longitude=float(mapa["longitude"].mean()), zoom=1)
    st.pydeck_chart(pdk.Deck(layers=[capa], initial_view_state=vista, tooltip={"text": "Magnitud: {mag}\nLugar: {place}\nFecha: {time}"}))
    st.caption(f"{len(mapa):,} sismos con coordenadas. {descripcion}")


def main() -> None:
    try:
        st.set_page_config(page_title="Reporte de terremotos", page_icon="🌍", layout="wide")
    except StreamlitAPIException:
        pass  # Ya fue configurada por inicio.py al usarse como subpágina.
    st.title("🌍 Reporte de terremotos")

    archivos = listar_archivos_datos()
    if not archivos:
        st.error(
            f"No se encontraron archivos `{PATRON_DATOS}` en `{CARPETA_DATOS}/`. "
            "Verifica que los CSV de terremotos estén en esa carpeta."
        )
        st.stop()

    st.caption("Análisis basado en " + ", ".join(f"`{archivo.name}`" for archivo in archivos) + ".")

    datos = cargar_datos(tuple(str(archivo) for archivo in archivos))
    fecha_minima = datos["time"].dt.date.min()
    fecha_maxima = datos["time"].dt.date.max()

    with st.sidebar:
        st.header("Filtros")
        fechas = st.date_input(
            "Período", value=(fecha_minima, fecha_maxima), min_value=fecha_minima, max_value=fecha_maxima
        )
        magnitud_minima = st.number_input("Magnitud mínima", min_value=0.0, value=2.5, step=0.1)

    if len(fechas) != 2:
        st.info("Selecciona una fecha de inicio y una de fin.")
        st.stop()

    inicio, fin = pd.Timestamp(fechas[0], tz="UTC"), pd.Timestamp(fechas[1], tz="UTC") + pd.Timedelta(days=1)
    filtrados = datos.loc[
        (datos["time"] >= inicio) & (datos["time"] < fin) & (datos["mag"] >= magnitud_minima)
    ].copy()

    if filtrados.empty:
        st.warning("No hay sismos que cumplan los filtros elegidos.")
        st.stop()

    filtrados["año"] = filtrados["time"].dt.year
    filtrados["hora"] = filtrados["time"].dt.hour
    filtrados["día de semana"] = filtrados["time"].dt.day_name().map({
        "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles", "Thursday": "Jueves",
        "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo",
    })
    filtrados["mes"] = filtrados["time"].dt.month_name().map({
        "January": "Enero", "February": "Febrero", "March": "Marzo", "April": "Abril",
        "May": "Mayo", "June": "Junio", "July": "Julio", "August": "Agosto",
        "September": "Septiembre", "October": "Octubre", "November": "Noviembre", "December": "Diciembre",
    })
    filtrados["rango de magnitud"] = filtrados["mag"].map(etiqueta_rango)
    filtrados["hemisferio norte/sur"] = filtrados["latitude"].map(
        lambda x: clasificar_hemisferio(x, "Norte", "Sur", "Ecuador")
    )
    filtrados["hemisferio este/oeste"] = filtrados["longitude"].map(
        lambda x: clasificar_hemisferio(x, "Este", "Oeste", "Greenwich")
    )

    pestaña_resumen, pestaña_mapa = st.tabs(["📊 Resumen", "🗺️ Mapa"])
    with pestaña_resumen:
        mostrar_resumen(filtrados)
    with pestaña_mapa:
        mostrar_mapa(filtrados)
    return

    columna1, columna2, columna3 = st.columns(3)
    columna1.metric("Terremotos", f"{len(filtrados):,}".replace(",", "."))
    columna2.metric("Magnitud máxima", f"{filtrados['mag'].max():.1f}")
    columna3.metric("Años con registros", filtrados["año"].nunique())

    st.header("Cantidad de sismos por año")
    por_año = filtrados.groupby("año").size().rename("Cantidad")
    st.line_chart(por_año)

    st.header("Cantidad por año y rango de magnitud")
    por_año_magnitud = pd.crosstab(filtrados["año"], filtrados["rango de magnitud"])
    orden_rangos = sorted(por_año_magnitud.columns, key=lambda x: float(x.split(",")[0]))
    st.bar_chart(por_año_magnitud[orden_rangos])

    st.header("Patrones temporales")
    por_hora = filtrados.groupby("hora").size().reindex(range(24), fill_value=0).rename("Cantidad")
    orden_días = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    por_día = filtrados.groupby("día de semana").size().reindex(orden_días, fill_value=0).rename("Cantidad")
    orden_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    por_mes = filtrados.groupby("mes").size().reindex(orden_meses, fill_value=0).rename("Cantidad")
    hora, día, mes = st.columns(3)
    hora.subheader("Por hora del día (UTC)")
    hora.bar_chart(por_hora)
    día.subheader("Por día de la semana")
    día.bar_chart(por_día)
    mes.subheader("Por mes del año")
    mes.bar_chart(por_mes)

    st.header("Distribución por hemisferio")
    norte_sur = filtrados.groupby("hemisferio norte/sur").size().rename("Cantidad")
    este_oeste = filtrados.groupby("hemisferio este/oeste").size().rename("Cantidad")
    izquierda, derecha = st.columns(2)
    izquierda.bar_chart(norte_sur)
    derecha.bar_chart(este_oeste)
    st.caption("La latitud define Norte/Sur y la longitud define Este/Oeste. Los valores 0 se muestran como Ecuador o Greenwich.")

    st.header("Top 10 sismos de mayor magnitud")
    columnas = ["time", "año", "mag", "latitude", "longitude", "place"]
    disponibles = [columna for columna in columnas if columna in filtrados.columns]
    top_10 = filtrados.nlargest(10, "mag")[disponibles].copy()
    top_10 = top_10.rename(columns={"time": "Fecha y hora (UTC)", "año": "Año", "mag": "Magnitud", "latitude": "Latitud", "longitude": "Longitud", "place": "Lugar"})
    st.dataframe(top_10, hide_index=True, use_container_width=True)


if __name__ == "__main__":
    main()
