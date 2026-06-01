import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime
import time
import random
import sys
import os

# Configuración de rutas para importar módulos locales
base_path = os.path.dirname(os.path.abspath(__file__))
if base_path not in sys.path:
    sys.path.insert(0, base_path)

try:
    from schema_seguridad import LogEntrada
    from database_manager import inicializar_db, guardar_evento
    from analizador_ml import MotorDecision
except ImportError as e:
    st.error(f"Error al cargar módulos del sistema: {e}")
    st.stop()

# Configuración de la página
st.set_page_config(
    page_title="SentinelAI - NIDS Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar base de datos y motor de IA
inicializar_db()

@st.cache_resource
def cargar_motor():
    """Instancia el motor de ML una sola vez para ahorrar recursos."""
    return MotorDecision()

motor = cargar_motor()

# --- Funciones de Datos ---
def obtener_datos():
    """Recupera los logs desde SQLite de forma segura."""
    try:
        conn = sqlite3.connect('sentinel_logs.db')
        df = pd.read_sql_query("SELECT * FROM logs ORDER BY timestamp DESC", conn)
        conn.close()
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        return pd.DataFrame()

def ejecutar_simulacion(n_eventos=20):
    """Genera tráfico sintético y lo procesa a través del motor de IA."""
    ips_fijas = ["192.168.1.50", "192.168.1.100", "192.168.1.150", "192.168.1.200"]
    for _ in range(n_eventos):
        data = {
            "ip_origen": random.choice(ips_fijas),
            "intentos_fallidos": random.randint(1, 25),
            "protocolo": random.choice(["SSH", "HTTP", "HTTPS", "FTP"]),
            "timestamp": datetime.now()
        }
        try:
            log = LogEntrada(**data)
            decision = motor.generar_reporte(log)
            guardar_evento(log, decision.nivel_riesgo)
        except Exception:
            continue

# --- Interfaz de Usuario (Sidebar) ---
with st.sidebar:
    st.title("🛡️ SentinelAI Panel")
    st.markdown("---")

    st.subheader("🚀 Simulación de Tráfico")
    st.write("Genera eventos de red para poner a prueba el motor de IA.")
    num_eventos = st.slider("Eventos a generar", 5, 100, 20)
    if st.button("Lanzar Simulación", use_container_width=True):
        with st.spinner("Motor de IA analizando..."):
            ejecutar_simulacion(num_eventos)
        st.toast(f"✅ {num_eventos} eventos procesados exitosamente.")
        time.sleep(0.5)
        st.rerun()

    st.markdown("---")
    st.subheader("⚙️ Configuración")
    auto_refresh = st.checkbox("Auto-refrescar (5s)", value=True)

    st.markdown("---")
    st.info("**SentinelAI** utiliza un modelo de **Isolation Forest** para identificar anomalías estadísticas en el tráfico local.")

# --- Dashboard Principal ---
st.title("SentinelAI: Predictive Network Intrusion Detection System")
st.caption(f"Monitoreo de Seguridad Inteligente | Estado del Motor: [ACTIVO] | Última actualización: {datetime.now().strftime('%H:%M:%S')}")

df = obtener_datos()

if df.empty:
    st.warning("⚠️ **Base de datos vacía.** Por favor, utiliza el botón 'Lanzar Simulación' en el panel lateral para generar tráfico de prueba.")
else:
    # Métricas Clave
    m1, m2, m3, m4 = st.columns(4)

    total = len(df)
    criticos = len(df[df['riesgo'] == 'CRITICO'])
    medios = len(df[df['riesgo'] == 'MEDIO'])
    bajos = len(df[df['riesgo'] == 'BAJO'])

    m1.metric("Total Eventos", total)
    m2.metric("Alertas CRÍTICAS", criticos, delta=f"{criticos/total*100:.1f}%", delta_color="inverse")
    m3.metric("Riesgo MEDIO", medios)
    m4.metric("Tráfico SEGURO", bajos)

    st.markdown("---")

    # Gráficos de analytics
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📊 Distribución de Riesgos")
        fig_pie = px.pie(
            df, names='riesgo',
            color='riesgo',
            color_discrete_map={'CRITICO': '#EF553B', 'MEDIO': '#FECB52', 'BAJO': '#00CC96'},
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_right:
        st.subheader("🌐 Protocolos Detectados")
        fig_bar = px.bar(
            df['protocolo'].value_counts().reset_index(),
            x='index', y='count',
            labels={'index': 'Protocolo', 'count': 'Frecuencia'},
            color='index',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    st.subheader("📈 Cronología de Amenazas (Eventos/Minuto)")

    df_time = df.copy()
    df_time['minuto'] = df_time['timestamp'].dt.floor('min')
    df_agg = df_time.groupby(['minuto', 'riesgo']).size().reset_index(name='conteo')

    fig_line = px.line(
        df_agg, x='minuto', y='conteo', color='riesgo',
        color_discrete_map={'CRITICO': '#EF553B', 'MEDIO': '#FECB52', 'BAJO': '#00CC96'},
        line_shape="spline"
    )
    st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 Registro de Seguridad (Últimos 50 eventos)")

    def color_riesgo(val):
        color = 'red' if val == 'CRITICO' else 'orange' if val == 'MEDIO' else 'green'
        return f'color: {color}; font-weight: bold'

    st.dataframe(
        df.head(50).style.applymap(color_riesgo, subset=['riesgo']),
        use_container_width=True,
        hide_index=True
    )

# Lógica de auto-refresco controlada
if auto_refresh:
    time.sleep(5)
    st.rerun()
