"""Análisis básico de cantidad de sismos por año e intervalo de magnitud.

Requiere pandas:
    py -m pip install pandas

Uso:
    py analizar_sismos.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


CARPETA_DATOS = Path("data")
PATRON_ENTRADA = "terremotos_*.csv"
ARCHIVO_SALIDA = Path("data/sismos_por_anio_intensidad.csv")


def crear_intervalos(maxima_magnitud: float) -> tuple[list[float], list[str]]:
    """Devuelve intervalos 2,5–3,5; 3,5–4,5; etc., hasta el máximo hallado."""
    limite_superior = max(3.5, float(int(maxima_magnitud - 2.5) + 3.5))
    bordes = [2.5 + indice for indice in range(int(limite_superior - 2.5) + 1)]
    etiquetas = [f"{borde:.1f} - {borde + 1:.1f}".replace(".", ",") for borde in bordes[:-1]]
    return bordes, etiquetas


def main() -> None:
    archivos = sorted(CARPETA_DATOS.glob(PATRON_ENTRADA))
    if not archivos:
        raise FileNotFoundError(
            f"No se encontraron archivos '{PATRON_ENTRADA}' en '{CARPETA_DATOS}'."
        )

    datos = pd.concat(
        (pd.read_csv(archivo, usecols=["time", "mag"]) for archivo in archivos), ignore_index=True
    )
    datos["time"] = pd.to_datetime(datos["time"], errors="coerce", utc=True)
    datos["mag"] = pd.to_numeric(datos["mag"], errors="coerce")
    datos = datos.dropna(subset=["time", "mag"])
    datos = datos[datos["mag"] >= 2.5].copy()

    if datos.empty:
        print("No hay sismos con magnitud igual o superior a 2,5.")
        return

    bordes, etiquetas = crear_intervalos(datos["mag"].max())
    datos["año"] = datos["time"].dt.year
    datos["intensidad"] = pd.cut(
        datos["mag"], bins=bordes, labels=etiquetas, right=False, include_lowest=True
    )

    tabla = pd.crosstab(datos["año"], datos["intensidad"], dropna=False)
    tabla["Total"] = tabla.sum(axis=1)
    tabla.loc["Total"] = tabla.sum(axis=0)

    ARCHIVO_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(ARCHIVO_SALIDA, encoding="utf-8-sig")

    print("Cantidad de sismos por año e intensidad:\n")
    print(tabla.to_string())
    print(f"\nResultado guardado en: {ARCHIVO_SALIDA}")


if __name__ == "__main__":
    main()
