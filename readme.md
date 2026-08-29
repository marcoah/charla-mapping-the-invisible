# Mapping the Invisible: Spatial Data Evolution and Seismology

Este repositorio y espacio de trabajo consolidan el análisis de cómo **las geociencias han sido pioneras históricas en el análisis de datos complejos**, desde la cartografía espacial analógica del siglo XIX hasta los modernos pipelines de datos en la nube y aplicaciones interactivas en tiempo real.

El proyecto está diseñado como una guía estratégica y de apoyo visual para la entrevista técnica en el canal de YouTube **deztaca**.

---

## 🐍 Scripts de Python

| Script | Qué hace | Cómo se ejecuta |
| --- | --- | --- |
| [`combinar_csv.py`](combinar_csv.py) | Une varios CSV con el mismo encabezado en uno solo (por defecto lee `data/*.csv` y escribe `data/terremotos_combinados.csv`). Se usó para producir los CSV de `terremotos_*` a partir de las descargas crudas del catálogo. | `py combinar_csv.py --carpeta <origen> --salida <destino.csv>` |
| [`analizar_sismos.py`](analizar_sismos.py) | Lee todos los `data/terremotos_*.csv`, agrupa por año y rango de magnitud (cada 1.0, empezando en 2,5) y guarda la tabla resultante en `data/sismos_por_anio_intensidad.csv`. | `py analizar_sismos.py` |
| [`inicio.py`](inicio.py) | **Punto de entrada recomendado.** App multipágina de Streamlit: página de inicio con accesos directos, más los reportes 1 y 2 en el menú lateral. | `py -m streamlit run inicio.py` |
| [`reporte_sismos.py`](reporte_sismos.py) | **Reporte 1** (también funciona como app independiente): carga todos los `data/terremotos_*.csv`, permite filtrar por fecha y magnitud mínima, y muestra métricas, gráficos temporales y un mapa (puntos o calor) con pydeck. | `py -m streamlit run reporte_sismos.py` |
| [`reporte_cubos_3d.py`](reporte_cubos_3d.py) | **Reporte 2** (también funciona como app independiente): grafica los sismos de México, Perú y Venezuela como cubos 3D con matplotlib (X = longitud, Y = latitud, Z = profundidad), cada uno con su mapa correspondiente debajo. La selección de cada país es una caja delimitadora aproximada, no su contorno político exacto. | `py -m streamlit run reporte_cubos_3d.py` |

Instalación de dependencias (ver [`requirements.txt`](requirements.txt)):

```sh
py -m pip install -r requirements.txt
```

---

## 📁 Datos (`data/`)

Los archivos `terremotos_*.csv` contienen el catálogo sísmico completo (1900–actualidad, formato estilo USGS) **partido en varios archivos por rango de años** para mantener cada uno por debajo del límite de tamaño de GitHub. Todos comparten el mismo encabezado:

`time, latitude, longitude, depth, mag, magType, nst, gap, dmin, rms, net, id, updated, place, type, horizontalError, depthError, magError, magNst, status, locationSource, magSource`

- `combinar_csv.py` y `analizar_sismos.py` leen **todos** los archivos que calcen con el patrón `terremotos_*.csv`, así que el número o los rangos de estos archivos pueden cambiar (partirse o reagruparse) sin romper los scripts.
- `terremotos_completo_1900-2026.rar` es el catálogo unificado comprimido (equivalente a concatenar todos los `terremotos_*.csv`); solo se usa para distribución/backup, no lo leen los scripts.
- `sismos_por_anio_intensidad.csv` es un archivo **derivado**, generado por `analizar_sismos.py` (no es una fuente cruda ni sigue el patrón `terremotos_*`).

---

## 🚀 Mensaje Central (The "So What?")

**La Tierra es la base de datos física más grande de la historia y el geólogo es su ingeniero de datos.** Las rocas registran información ininterrumpida; nuestro trabajo es estructurarla, procesarla y aplicar algoritmos de visualización y estimación espacial para resolver problemas críticos de sismología, prevención de desastres y optimización comercial.

---

## 🗺️ Estructura del Contenido y Hilos Narrativos

El proyecto se desglosa en los siguientes ejes conceptuales:

### 1. La Tierra como Base de Datos (`SQL` en las Rocas)

- **Estratos de roca:** Registros individuales (filas en una base de datos).
- **Tamaño de grano:** Variable cuantitativa que mide la energía del ambiente antiguo.
- **Fósiles guía:** Marcas de tiempo (_timestamps_) y metadatos geológicos.
- **Fallas y discordancias:** Anomalías físicas e interrupciones del sistema (_data gaps_).

### 2. Sismología Moderna: Pipelines en la Nube y Alerta Temprana

- **Ingestión en Streaming:** Procesamiento de señales continuas de sismógrafos en milisegundos con **AWS Kinesis** y **Azure Event Hubs**.
- **ETL & Procesamiento:** Filtrado de ruido con **Python** (librerías `pandas` y `ObsPy`).
- **Almacenamiento Espacial:** Bases de datos indexadas con **PostgreSQL + PostGIS** y lagos de datos eficientes en formato **Parquet**.
- **La carrera contra la latencia:** Cómo el envío de alertas digitales a la velocidad de la luz (300,000 km/s) supera físicamente a las destructivas Ondas S (3-4 km/s) para salvar vidas en tiempo real.
- **Visualización:** Análisis del dataset de terremotos (1900-2026) mediante un reporte interactivo en **Streamlit**.

### 3. Hitos de la Visualización de Datos Espaciales

- **John Snow (1854):** El primer análisis espacial de la historia. Mapeo de muertes por cólera y bombas de agua en el Soho, demostrando que **los datos atípicos (anomalías)** como la cervecería sin muertes y la viuda lejana infectada validan las hipótesis científicas.
- **Alfred Wegener (1912):** Integración transdisciplinaria de "Big Data Analógica" (paleoclimatología, paleontología y morfología). La lección de que **una correlación perfecta no es suficiente si falta un algoritmo o mecanismo físico**.
- **Marie Tharp (1950s):** _Data wrangling_ analógico de perfiles unidimensionales de sonar para mapear el fondo marino en 3D. El momento "Eureka" al hacer un **data join** con el mapa de sismicidad global de Howard Foster, revelando que los terremotos se alinean con el valle de rift, probando la tectónica de placas.

### 4. Transferencia Tecnológica: Del Oro a Starbucks

- **Kriging (1951):** El Mejor Estimador Lineal Insesgado (BLUE) espacial, inventado por Danie Krige para evaluar minas de oro reduciendo el riesgo financiero de excavar a ciegas basándose en la autocorrelación espacial.
- **Geomarketing comercial:** Cómo **Starbucks** y **Dunkin' Donuts** usan Sistemas de Información Geográfica (SIG) y modelos espaciales de tráfico y demografía para predecir las ventas de una sucursal antes de abrirla.
- **Análisis Multivariado (PCA):** Del análisis geotécnico y clasificación de suelos a la segmentación de millones de clientes en plataformas de _e-commerce_.

---

## 📂 Entregables Disponibles en el Panel de Estudio

Este espacio de trabajo contiene los siguientes artefactos listos para su uso y descarga:

1.  **`guia-geociencias-datos-storytelling-v3.docx`**  
    _Guía escrita completa (Word)_. Diseñada capítulo por capítulo como documento maestro de preparación para repasar antes de la transmisión. Incluye esquemas, resúmenes históricos y fundamentos matemáticos.
2.  **`Geociencias y Datos: El Arte de Leer la Tierra (v3)`**  
    _Presentación de Diapositivas_. Estructurada bajo el orden lógico refinado (comenzando con sismología moderna e ingeniería de datos en la nube) para proyectar y apoyar visualmente la entrevista en vivo.
3.  **`Research report: Geociencias, Datos y Storytelling Sismológico`**  
    _Reporte de Investigación Base_. Documento de respaldo técnico e histórico integrado en tus Fuentes para realizar consultas rápidas en el chat.
