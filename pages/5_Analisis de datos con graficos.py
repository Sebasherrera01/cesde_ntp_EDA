import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Actividad: Descubriendo los Datos Reales", layout="wide")

# --- Estilo Personalizado ---
st.markdown("""
    <style>
    .main {
        background-color: #F3E5F5;
    }
    [data-testid="stSidebar"] {
        background-color: #F3E5F5;
    }
    .stButton > button {
        background-color: #E1BEE7;
        color: #4A148C;
        border-radius: 10px;
        border: 1px solid #9C27B0;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #9C27B0;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🧩 Actividad: ¿De qué se tratan estos datos?")
st.markdown("""
### Objetivo de la Actividad
Explorar con gráficos datos reales extraídos de fuentes abiertas o archivos CSV,
aplicando filtros y comparando columnas numéricas y categóricas.
""")

# --- Barra Lateral con Instrucciones e Interactividad ---
with st.container():
    st.header("📋 Guía para el análisis")
    st.info("""
    1. **Observa** los gráficos. ¿Qué tendencias aparecen?
    2. **Compara** entre columnas numéricas y categóricas.
    3. **Ajusta** cuántos registros quieres ver en las visualizaciones.
    4. **Reflexiona** sobre el contexto: fechas, municipios, valores monetarios, etc.
    """)
    
    st.markdown("---")
    uploaded_file = st.file_uploader("Sube un archivo CSV para investigar", type="csv")

    rows_to_plot = st.slider(
        "¿Cuántos registros quieres graficar?",
        min_value=5,
        max_value=100,
        value=20,
        step=5,
    )

@st.cache_data
def load_data(file):
    try:
        return pd.read_csv(file)
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return None

# Lógica de selección de archivo
df = None
if uploaded_file is not None:
    df = load_data(uploaded_file)
    if df is not None:
        st.success("Dataset cargado para el análisis.")

if df is not None:
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    cat_cols = df.select_dtypes(exclude=['number']).columns.tolist()
    rows_to_plot = min(rows_to_plot, len(df))

    with st.expander("🔧 Opciones de Gráficos", expanded=True):
        st.write("Selecciona qué columnas quieres incluir en las visualizaciones:")
        selected_numeric = st.multiselect("Columnas numéricas", num_cols, default=num_cols[:2])
        selected_categorical = st.multiselect("Columnas categóricas", cat_cols, default=cat_cols[:1])

    # --- Paso 1: Primer Impacto ---
    st.header("Step 1: 🔍 Primer Impacto (Inspección Visual)")
    st.markdown("Observa la composición del dataset y los primeros patrones en las columnas seleccionadas.")

    if selected_numeric:
        st.subheader("Tendencias en columnas numéricas")
        fig = px.line(df.head(rows_to_plot), y=selected_numeric, markers=True)
        fig.update_layout(height=400, legend_title_text='Columnas', title="Tendencia de Columnas Numéricas")
        st.plotly_chart(fig, use_container_width=True, key="numeric_trend_chart")
    else:
        st.info("Selecciona al menos una columna numérica para ver tendencias en los datos.")

    if selected_categorical:
        st.subheader("Frecuencias de categorías principales")
        for col in selected_categorical:
            counts = df[col].value_counts().head(10).reset_index()
            counts.columns = [col, 'frecuencia']
            fig = px.bar(counts, x=col, y='frecuencia', title=f"Top 10 de {col}")
            fig.update_layout(xaxis_title=col, yaxis_title='Frecuencia', height=400, title=f"Top 10 de {col}")
            st.plotly_chart(fig, use_container_width=True, key=f"cat_freq_chart_{col}")
    else:
        st.info("Selecciona al menos una columna categórica para ver distribuciones.")


    # --- Paso 2: La Estructura ---
    st.header("Step 2: 🏗️ La Estructura")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Filas totales", f"{df.shape[0]}")
        st.metric("Columnas totales", f"{df.shape[1]}")
    with col2:
        st.metric("Columnas numéricas", f"{len(num_cols)}")
        st.metric("Columnas categóricas", f"{len(cat_cols)}")
    with col3:
        dtype_counts = df.dtypes.astype(str).value_counts().reset_index()
        dtype_counts.columns = ['Tipo', 'Cantidad']
        dtype_fig = px.bar(dtype_counts, x='Tipo', y='Cantidad', title='Tipos de datos en el dataset')
        dtype_fig.update_layout(height=400, xaxis_title='Tipo de dato', yaxis_title='Cantidad', title="Distribución de Tipos de Datos")
        st.plotly_chart(dtype_fig, use_container_width=True, key="dtype_distribution_chart")

    with st.expander("💡 ¿Cómo interpretar la estructura?", expanded=False):
        st.write("""
        - **Filas:** Cada registro puede representar un evento, una persona, un reporte o una transacción.
        - **Columnas:** Cada característica describe un aspecto distinto del fenómeno.
        - **Tipos de datos:** Si hay muchas columnas `object`, probablemente haya nombres, códigos o ubicaciones.
        """)

    # --- Paso 3: Calidad y Vacíos ---
    st.header("Step 3: ❗ Calidad y Vacíos")
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if not missing.empty:
        st.subheader("Columnas con valores faltantes")
        missing_fig = px.bar(missing.reset_index(), x='index', y=missing.name, title='Valores faltantes por columna')
        missing_fig.update_layout(height=400, xaxis_title='Columna', yaxis_title='Cantidad de nulos', title="Valores Faltantes por Columna")
        st.plotly_chart(missing_fig, use_container_width=True, key="missing_values_chart")
        st.markdown("💡 *Pregunta: ¿Por qué crees que faltan datos en esas columnas específicas?*")
    else:
        st.success("Este dataset está completo. No faltan datos.")

    with st.expander("💡 ¿Qué significan los datos faltantes?", expanded=False):
        st.write("""
        - **Nulos (NaN):** Indican valores que no se recolectaron o no aplican.
        - **Impacto:** Un gran número de nulos en columnas clave puede deformar las conclusiones.
        - **Sesgo:** Si solo faltan datos para ciertos grupos, el análisis puede estar parcializado.
        """)

    # --- Paso 4: El Corazón de los Datos ---
    st.header("Step 4: 📈 El Corazón de los Datos")

    if selected_numeric:
        st.subheader("Análisis cuantitativo")
        stats = df[selected_numeric].describe().transpose()[['mean', '50%', 'std', 'min', 'max']]
        st.markdown("**Resumen estadístico de las columnas numéricas seleccionadas**")
        stats_fig = px.bar(stats.reset_index(), x='index', y=['mean', 'std'], barmode='group', title='Media y Desviación Estándar')
        stats_fig.update_layout(xaxis_title='Columna', yaxis_title='Valor', height=450, title="Media y Desviación Estándar de Columnas Numéricas")
        st.plotly_chart(stats_fig, use_container_width=True, key="quantitative_stats_chart")

        st.markdown(f"**Tendencia de los primeros {rows_to_plot} registros**")
        trend_fig = px.line(df.head(rows_to_plot), y=selected_numeric, markers=True)
        trend_fig.update_layout(height=450, legend_title_text='Columnas', title=f"Tendencia de los Primeros {rows_to_plot} Registros")
        st.plotly_chart(trend_fig, use_container_width=True, key="quantitative_trend_chart")
    else:
        st.info("Selecciona columnas numéricas para ver los gráficos cuantitativos.")

    if selected_categorical:
        st.subheader("Análisis cualitativo")
        for col in selected_categorical:
            st.markdown(f"**Distribución de '{col}'**")
            counts = df[col].value_counts().head(10).reset_index()
            counts.columns = [col, 'frecuencia']
            fig = px.bar(counts, x=col, y='frecuencia', title=f"Distribución de '{col}' (Top 10)")
            fig.update_layout(height=400, xaxis_title=col, yaxis_title='Frecuencia', title=f"Distribución de '{col}' (Top 10)")
            st.plotly_chart(fig, use_container_width=True, key=f"qualitative_dist_chart_{col}")
    else:
        st.info("Selecciona columnas categóricas para ver los gráficos cualitativos.")


    # --- Conclusiones de Investigación ---
    st.header("📝 Resumen del análisis")
    st.markdown(f"""
    ### 🕵️ Informe del detective
    Basado en tu investigación, aquí hay un resumen de lo encontrado:
    * **Volumen:** Estás manejando **{df.shape[0]} registros**.
    * **Variables:** El dataset contiene **{len(cat_cols)} columnas de texto** y **{len(num_cols)} columnas numéricas**.
    * **Análisis visual:** Usa los gráficos interactivos para comparar tendencias en los primeros **{rows_to_plot} registros**.
    """)

    st.divider()
    st.header("✍️ Conclusiones finales")
    st.markdown("Escribe tus hallazgos principales después de revisar los gráficos.")
    conclusiones_graficos = st.text_area(
        "¿Qué conclusiones obtienes de los datos?",
        placeholder="Ej: La mayoría de los registros corresponde a un mismo municipio y las columnas numéricas muestran...",
        height=150,
        key="conclusiones_graficos",
    )
    if conclusiones_graficos.strip():
        with st.expander("Vista previa de tus conclusiones", expanded=False):
            st.markdown(conclusiones_graficos)
        st.download_button(
            label="📥 Descargar conclusiones (.txt)",
            data=conclusiones_graficos,
            file_name="conclusiones_analisis_graficos.txt",
            mime="text/plain",
        )
else:
    st.warning("sube un archivo CSV para hacer el analisis como tal ")

st.title("Estudiantes por Programa Académico")
programas = (
    df["PROGRAMA"]
    .value_counts()
    .reset_index()
)

programas.columns = ["Programa Académico", "Cantidad de Estudiantes"]


st.subheader("Filtros")

col1, col2, col3 = st.columns(3)

with col1:
    orden = st.selectbox(
        "Ordenar por cantidad",
        ["Mayor a menor", "Menor a mayor"]
    )

with col2:
    top_n = st.slider(
        "Cantidad de programas",
        min_value=5,
        max_value=len(programas),
        value=15
    )

with col3:
    min_est = int(programas["Cantidad de Estudiantes"].min())
    max_est = int(programas["Cantidad de Estudiantes"].max())

    rango = st.slider(
        "Rango de estudiantes",
        min_value=min_est,
        max_value=max_est,
        value=(min_est, max_est)
    )

programas_filtrados = programas[
    (programas["Cantidad de Estudiantes"] >= rango[0]) &
    (programas["Cantidad de Estudiantes"] <= rango[1])
]

ascending = orden == "Menor a mayor"

programas_filtrados = programas_filtrados.sort_values(
    by="Cantidad de Estudiantes",
    ascending=ascending
)

programas_filtrados = programas_filtrados.head(top_n)

fig = px.bar(
    programas_filtrados,
    x="Cantidad de Estudiantes",
    y="Programa Académico",
    orientation="h",
    text="Cantidad de Estudiantes",
    title="Cantidad de estudiantes por programa"
)

fig.update_layout(
    height=700
)

if not ascending:
    fig.update_layout(
        yaxis=dict(autorange="reversed")
    )

st.plotly_chart(fig, use_container_width=True)

# -------- ------------

st.write(df.columns.tolist())

# -------- ------------

st.title("Distribución por Sexo Biológico")

sexo = (
    df["SEXO BIOLOGICO"]
    .value_counts()
    .reset_index()
)
sexo.columns = ["Sexo", "Cantidad"]

fig = px.pie(
    sexo,
    names="Sexo",
    values="Cantidad",
    title="Distribución de estudiantes por sexo",
    hole=0.4
)

fig.update_traces(
    textposition='inside',
    textinfo='percent+label'
)

st.plotly_chart(fig, use_container_width=True)

# -------- ------------

st.title("Tasa de aprobación por programa académico")

df["PROGRAMA"] = df["PROGRAMA"].astype(str).str.strip()

df = df[df["NUMERO MATERIAS INSCRITAS"] > 0]

df["TASA APROBACION"] = (
    df["NUMERO MATERIAS APROBADAS"] / df["NUMERO MATERIAS INSCRITAS"]
) * 100

tasa_programa = (
    df.groupby("PROGRAMA")
    .agg(
        Tasa_Aprobacion=("TASA APROBACION", "mean"),
        Estudiantes=("PROGRAMA", "count"),
        Materias_Inscritas=("NUMERO MATERIAS INSCRITAS", "sum"),
        Materias_Aprobadas=("NUMERO MATERIAS APROBADAS", "sum")
    )
    .reset_index()
)

tasa_programa.columns = [
    "Programa Académico",
    "Tasa de Aprobación",
    "Cantidad de Estudiantes",
    "Materias Inscritas",
    "Materias Aprobadas"
]

st.subheader("Filtros")

col1, col2, col3 = st.columns(3)

with col1:
    orden = st.selectbox(
        "Ordenar por tasa",
        ["Mayor a menor", "Menor a mayor"]
    )

with col2:
    top_n = st.slider(
        "Cantidad de programas",
        min_value=5,
        max_value=len(tasa_programa),
        value=15
    )

with col3:
    rango_tasa = st.slider(
        "Rango de tasa de aprobación",
        min_value=0,
        max_value=100,
        value=(0, 100)
    )

col4, col5 = st.columns(2)

with col4:
    min_estudiantes = st.slider(
        "Mínimo de estudiantes por programa",
        min_value=1,
        max_value=int(tasa_programa["Cantidad de Estudiantes"].max()),
        value=1
    )

with col5:
    programa_buscar = st.text_input(
        "Buscar programa académico"
    )

tasa_filtrada = tasa_programa[
    (tasa_programa["Tasa de Aprobación"] >= rango_tasa[0]) &
    (tasa_programa["Tasa de Aprobación"] <= rango_tasa[1]) &
    (tasa_programa["Cantidad de Estudiantes"] >= min_estudiantes)
]

if programa_buscar:
    tasa_filtrada = tasa_filtrada[
        tasa_filtrada["Programa Académico"]
        .str.contains(programa_buscar, case=False, na=False)
    ]

ascending = orden == "Menor a mayor"

tasa_filtrada = tasa_filtrada.sort_values(
    by="Tasa de Aprobación",
    ascending=ascending
)

tasa_filtrada = tasa_filtrada.head(top_n)

fig = px.bar(
    tasa_filtrada,
    x="Tasa de Aprobación",
    y="Programa Académico",
    orientation="h",
    text=tasa_filtrada["Tasa de Aprobación"].round(2),
    title="Tasa de aprobación promedio por programa académico",
    hover_data=[
        "Cantidad de Estudiantes",
        "Materias Inscritas",
        "Materias Aprobadas"
    ]
)

fig.update_traces(
    texttemplate="%{text}%",
    textposition="outside"
)

fig.update_layout(
    height=700,
    xaxis_title="Tasa de aprobación (%)",
    yaxis_title="Programa Académico"
)

if not ascending:
    fig.update_layout(
        yaxis=dict(autorange="reversed")
    )

st.plotly_chart(fig, use_container_width=True)
    st.warning("Sube un archivo CSV para comenzar el análisis con gráficos.")
