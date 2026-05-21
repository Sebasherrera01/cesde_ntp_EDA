import streamlit as st
import pandas as pd
import requests
import altair as alt

# Configuración de la página
st.set_page_config(page_title="Gestión Corporativa Colombia - API Real", layout="wide")

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

st.title("Knowly")
st.markdown("""
### Objetivo
En esta sección, consumiremos **usuarios** desde la API real de Knowly.
Los datos incluyen información sobre la organización (rol, nombre, documento, correo, etc.).
""")

API_BASE_URL = "https://knowly-back-10.onrender.com/usuario"

API_ERROR_MESSAGES = {
    "timeout": "⏱️ La API tardó demasiado en responder.",
    "connection": "🌐 No se pudo conectar con el servidor.",
    "unexpected": "❌ Error inesperado.",
}

if st.button("🔄 Refrescar Datos (Limpiar Caché)"):
    st.cache_data.clear()
    st.rerun()


@st.cache_data
def get_api_data():
    """Devuelve (DataFrame, código_de_error). None si la carga fue exitosa."""
    try:
        response = requests.get(API_BASE_URL, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return pd.DataFrame(data), None
            return pd.DataFrame([data]), None
        return pd.DataFrame(), f"http_{response.status_code}"
    except requests.exceptions.Timeout:
        return pd.DataFrame(), "timeout"
    except requests.exceptions.ConnectionError:
        return pd.DataFrame(), "connection"
    except Exception:
        return pd.DataFrame(), "unexpected"


def post_usuario_data(data):
    try:
        response = requests.post(API_BASE_URL, json=data, timeout=10)
        if response.status_code in (200, 201):
            st.success("Usuario enviado exitosamente a la API.")
            return True
        st.error(f"Error al enviar: Status {response.status_code}")
        try:
            st.json(response.json())
        except Exception:
            st.error(response.text)
        return False
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return False


def put_usuario_data(data, usuario_id):
    try:
        endpoint = f"{API_BASE_URL}/{usuario_id}"
        response = requests.put(endpoint, json=data, timeout=10)
        if response.status_code in (200, 201, 204):
            st.success("Usuario actualizado exitosamente en la API.")
            if response.text:
                content_type = response.headers.get("content-type", "")
                if content_type.startswith("application/json"):
                    st.json(response.json())
                else:
                    st.write(response.text)
            return True
        st.error(f"Error al actualizar: Status {response.status_code}")
        if response.text:
            st.write(response.text)
        return False
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return False


def show_api_error(api_error):
    if not api_error:
        return
    if api_error in API_ERROR_MESSAGES:
        st.error(API_ERROR_MESSAGES[api_error])
    elif api_error.startswith("http_"):
        st.error(f"Error: Status {api_error.replace('http_', '')}")
    else:
        st.error(api_error)
    st.warning(
        "No se pudo conectar con la API. En Render el servidor puede tardar unos segundos "
        "en despertar. Espera un momento y pulsa **Refrescar Datos (Limpiar Caché)**."
    )


with st.spinner("Conectando con la API..."):
    df_usuario, api_error = get_api_data()

show_api_error(api_error)

# --- Gráfica Inicial ---
st.subheader("📊 Gráfica inicial de datos obtenidos")
if not df_usuario.empty:
    if "rol" in df_usuario.columns:
        role_counts = df_usuario["rol"].value_counts().reset_index()
        role_counts.columns = ["Rol", "Cantidad"]
        chart = alt.Chart(role_counts).mark_bar().encode(
            x="Rol",
            y="Cantidad",
            color="Rol",
        ).properties(title="Distribución inicial de Roles de Usuario")
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info('No hay campo "rol" para graficar.')
else:
    st.info("💡 No se pudieron obtener datos para la gráfica inicial.")

# --- Sección 1: Gestión de Usuario ---
st.header("👥 Información del Usuario")
st.markdown("Datos del usuario obtenido de la API")

if not df_usuario.empty:
    st.subheader("Análisis del Usuario")
    if len(df_usuario) == 1:
        user = df_usuario.iloc[0]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("ID Usuario", user["ideusuario"])
        with col2:
            st.metric("Rol", user["rol"])
        with col3:
            st.metric("Nombre Completo", f"{user['nombre']} {user['apellido']}")

        c1, c2 = st.columns(2)
        with c1:
            st.metric("Documento", user["documento"])
        with c2:
            st.metric("Correo Electrónico", user["correo"])

        st.subheader("Visualización de Datos del Usuario")
        fields = ["nombre", "apellido", "correo"]
        lengths = [len(str(user[field])) for field in fields]
        chart_data = pd.DataFrame({"Campo": fields, "Longitud": lengths})
        chart = alt.Chart(chart_data).mark_bar().encode(
            x="Campo",
            y="Longitud",
            color="Campo",
        ).properties(title="Longitud de Campos de Texto")
        st.altair_chart(chart, use_container_width=True)

        st.subheader("Tabla del usuario")
        st.dataframe(df_usuario, use_container_width=True)

    else:
        st.subheader(" Panel de Análisis y Filtros Dinámicos")
        st.markdown("Usa los controles para segmentar la información y ver las métricas actualizadas.")

        col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
        with col_f1:
            roles_disponibles = sorted(df_usuario["rol"].unique().tolist())
            selected_roles = st.multiselect(
                " Seleccionar Roles:", roles_disponibles, default=roles_disponibles
            )
        with col_f2:
            search_term = st.text_input(" Buscar por Nombre/Apellido:", placeholder="Ej: Luis")
        with col_f3:
            doc_prefix = st.text_input(" Documento inicia con:", placeholder="Ej: 98")

        filtered_df = df_usuario.copy()
        if selected_roles:
            filtered_df = filtered_df[filtered_df["rol"].isin(selected_roles)]
        if doc_prefix:
            filtered_df = filtered_df[
                filtered_df["documento"].fillna("").astype(str).str.startswith(doc_prefix)
            ]
        if search_term:
            mask = (
                filtered_df["nombre"].str.contains(search_term, case=False)
                | filtered_df["apellido"].str.contains(search_term, case=False)
                | filtered_df["correo"].str.contains(search_term, case=False)
            )
            filtered_df = filtered_df[mask]

        m1, m2, m3 = st.columns(3)
        m1.metric("Usuarios filtrados", len(filtered_df))
        m2.metric("Total en Base de Datos", len(df_usuario))
        m3.metric(
            "🏷️ Roles Distintos",
            filtered_df["rol"].nunique() if not filtered_df.empty else 0,
        )

        st.subheader("📋 Tabla de usuarios (filtro aplicado)")
        st.dataframe(filtered_df, use_container_width=True)

        if not filtered_df.empty:
            st.subheader("📊 Análisis Gráfico de la Selección")
            col_chart1, col_chart2 = st.columns(2)

            with col_chart1:
                st.write("**Proporción por Rol**")
                role_dist = filtered_df["rol"].value_counts().reset_index()
                role_dist.columns = ["Rol", "Cantidad"]
                chart_pie = alt.Chart(role_dist).mark_arc(innerRadius=50).encode(
                    theta="Cantidad", color="Rol", tooltip=["Rol", "Cantidad"]
                ).properties(height=300)
                st.altair_chart(chart_pie, use_container_width=True)

            with col_chart2:
                st.write("**Nombres más frecuentes**")
                name_counts = filtered_df["nombre"].value_counts().head(5).reset_index()
                name_counts.columns = ["Nombre", "Frecuencia"]
                chart_names = alt.Chart(name_counts).mark_bar().encode(
                    x="Frecuencia",
                    y=alt.Y("Nombre", sort="-x"),
                    color="Nombre",
                    tooltip=["Nombre", "Frecuencia"],
                ).properties(height=300)
                st.altair_chart(chart_names, use_container_width=True)

else:
    st.info("💡 No se pudieron obtener datos del usuario de la API.")

# --- Crear Usuario (POST) ---
st.header("➕ Crear Nuevo Usuario")
st.markdown("Envía los datos de un nuevo usuario a la API usando el método POST")
with st.form("post_usuario_form"):
    post_id = st.text_input("ID Usuario", placeholder="Ej: 0009")
    post_rol = st.text_input("Rol", placeholder="Ej: ESTUDIANTE")
    post_nombre = st.text_input("Nombre", placeholder="Ej: Luis")
    post_apellido = st.text_input("Apellido", placeholder="Ej: Ramírez")
    post_documento = st.text_input("Documento", placeholder="Ej: 987654321")
    post_correo = st.text_input("Correo", placeholder="Ej: luisra@gmail.edu.com")
    post_password = st.text_input("Contraseña", type="password")
    submit_post = st.form_submit_button("Crear Usuario (POST)")

if submit_post:
    if not post_id or not post_nombre or not post_password:
        st.error("El ID, Nombre y Contraseña son campos obligatorios.")
    elif post_correo and "@" not in post_correo:
        st.error("Correo inválido")
    elif len(post_password) < 6:
        st.error("La contraseña debe tener mínimo 6 caracteres")
    else:
        post_data = {
            "ideusuario": post_id,
            "rol": post_rol,
            "nombre": post_nombre,
            "apellido": post_apellido,
            "documento": post_documento,
            "correo": post_correo,
            "contrasenia": post_password,
        }
        with st.spinner("Enviando datos..."):
            success = post_usuario_data(post_data)
        if success:
            st.cache_data.clear()
            st.rerun()

# --- Actualizar Usuario (PUT) ---
st.header("✏️ Actualizar Usuario")
st.markdown("Modifica un usuario existente usando su ID y el método PUT")
with st.form("put_usuario_form"):
    put_id = st.text_input("ID Usuario a actualizar", placeholder="Ej: 0001")
    put_rol = st.text_input("Rol", placeholder="Ej: ESTUDIANTE")
    put_nombre = st.text_input("Nombre", placeholder="Ej: Luis")
    put_apellido = st.text_input("Apellido", placeholder="Ej: Ramírez")
    put_documento = st.text_input("Documento", placeholder="Ej: 987654321")
    put_correo = st.text_input("Correo", placeholder="Ej: luisra@gmail.edu.com")
    put_password = st.text_input("Contraseña", type="password")
    submit_put = st.form_submit_button("Actualizar Usuario (PUT)")

if submit_put:
    if not put_id:
        st.error("El ID del usuario es obligatorio para actualizar.")
    elif put_correo and "@" not in put_correo:
        st.error("Correo inválido")
    elif put_password and len(put_password) < 6:
        st.error("La contraseña debe tener mínimo 6 caracteres")
    else:
        put_data = {
            "ideusuario": put_id,
            "rol": put_rol,
            "nombre": put_nombre,
            "apellido": put_apellido,
            "documento": put_documento,
            "correo": put_correo,
        }
        if put_password:
            put_data["contrasenia"] = put_password
        with st.spinner("Actualizando datos..."):
            success = put_usuario_data(put_data, put_id)
        if success:
            st.cache_data.clear()
            st.rerun()

st.info(f"""
**Detalles de la API:**
- **URL:** `{API_BASE_URL}`
- **Métodos:** GET para obtener datos, POST para crear usuario, PUT para actualizar usuario.
- **Nota:** El backend está alojado en **Render** (internet). Si no hay respuesta, espera unos segundos y usa el botón de refrescar.
""")
