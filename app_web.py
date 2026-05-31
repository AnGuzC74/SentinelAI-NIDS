import streamlit as st
import pandas as pd
import numpy as np
import os
import time
import random
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv
import plotly.express as px
from groq import Groq
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingRegressor

# Cargar variables de entorno
load_dotenv(override=True)
st.set_page_config(page_title="SentinelAI VZLA Pro", layout="wide", page_icon="🛡️")

# Inicialización de APIs y Conexiones Cloud
url_supabase = os.environ.get("SUPABASE_URL", "").strip()
key_supabase = os.environ.get("SUPABASE_KEY", "").strip()
API_GROQ = os.environ.get("GROQ_API_KEY", "").strip()
client_groq = Groq(api_key=API_GROQ) if API_GROQ else None

# Estilos visuales de alto contraste
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #0f172a; }
    div[data-testid="stMetric"] { background-color: #ffffff !important; border: 2px solid #cbd5e1 !important; padding: 20px !important; border-radius: 12px !important; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important; }
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] p { color: #1e293b !important; font-weight: 600 !important; font-size: 15px !important; opacity: 1.0 !important; white-space: normal !important; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] div { color: #0f172a !important; font-weight: 800 !important; font-size: 38px !important; }
    button[data-baseweb="tab"] { color: #475569 !important; font-weight: 600 !important; font-size: 16px !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #e63946 !important; border-bottom-color: #e63946 !important; }
    .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# ----------------------------------------------------------------------------------
# SIMULADOR EN VIVO INTEGRADO (CORRE SOLO CUANDO LA APP ESTÁ ABIERTA)
# ----------------------------------------------------------------------------------
NODOS_INFRAESTRUCTURA = [
    {"estado": "Caracas, DT", "lat": 10.48, "lon": -66.89, "peso_ataques": 0.50},
    {"estado": "Maracaibo, Zulia", "lat": 10.64, "lon": -71.61, "peso_ataques": 0.30},
    {"estado": "Valencia, Carabobo", "lat": 10.16, "lon": -68.00, "peso_ataques": 0.15},
    {"estado": "Barquisimeto, Lara", "lat": 10.06, "lon": -69.34, "peso_ataques": 0.05}
]
BOTNET_REPETITIVA = ["190.202.45.110", "201.244.18.92", "186.24.195.5", "200.11.205.14"]

def auto_inyectar_datos_frescos(supabase_client):
    """Inyecta ráfagas rápidas de simulación directo a Supabase al cargar la web"""
    # Genera 3 registros nuevos en cada recarga para dar la sensación de actualización constante
    for _ in range(3):
        nodo = random.choices(NODOS_INFRAESTRUCTURA, weights=[n["peso_ataques"] for n in NODOS_INFRAESTRUCTURA])[0]
        ip = random.choice(BOTNET_REPETITIVA) if random.random() > 0.3 else f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
        intentos = max(5, min(int((1.0 / (random.random() ** (1.0 / 1.5))) * 5), 120))
        protocolo = "Xmas-Scan/Exploit" if intentos > 70 else "SSH-Bruteforce"
        riesgo = "CRITICO" if intentos > 60 else ("ALTO" if intentos > 30 else "MEDIO")
        diagnostico = f"Ataque detectado en nodo mediante {protocolo}. Actividad anómala con {intentos} intentos fallidos."

        nuevo_log = {
            "ip_origen": ip, "intentos_fallidos": intentos, "protocolo": protocolo,
            "timestamp": datetime.now().isoformat(), "riesgo": riesgo, "diagnostico_ia": diagnostico,
            "estado": nodo["estado"], "lat": nodo["lat"], "lon": nodo["lon"]
    }
        try: supabase_client.table("logs_globales").insert(nuevo_log).execute()
        except: pass

def cargar_datos_portafolio():
    if not url_supabase or not key_supabase: return pd.DataFrame()
    try:
        supabase: Client = create_client(url_supabase, key_supabase)

        # El programa inyecta datos automáticamente al ser ejecutado/visitado
        auto_inyectar_datos_frescos(supabase)

        # Descarga los últimos 200 registros de Supabase para alimentar el mapa
        response = supabase.table("logs_globales").select("*").order("timestamp", desc=True).limit(200).execute()
        return pd.DataFrame(response.data)
    except:
        return pd.DataFrame()

# Carga de datos e inyección simultánea
df = cargar_datos_portafolio()

# ----------------------------------------------------------------------------------
# INTERFAZ SIDEBAR (CONSULTOR IA GROQ CLOUD)
# ----------------------------------------------------------------------------------
st.sidebar.title("🤖 Consultor de Incidentes IA (Groq Cloud)")
modelo_seleccionado = st.sidebar.selectbox("Escoge el motor de IA:", ["llama-3.3-70b-versatile", "llama3-8b-8192", "llama3-70b-8192"])
pregunta = st.sidebar.text_input("Escribe tu consulta de seguridad:")

if pregunta and client_groq and df is not None and not df.empty:
    with st.sidebar.spinner("Procesando en Groq..."):
        try:
            contexto_logs = ""
            for index, fila in df.head(15).iterrows():
                contexto_logs += f"- IP: {fila['ip_origen']} | Ubicación: {fila['estado']} | Riesgo: {fila['riesgo']} | Reporte Técnico: {fila['diagnostico_ia']}\n"
            prompt_completo = f"Eres un auditor forense experto. Responde basándote en estos logs:\n{contexto_logs}\nPregunta: {pregunta}"
            completion = client_groq.chat.completions.create(model=modelo_seleccionado, messages=[{"role": "user", "content": prompt_completo}], temperature=0.2, max_tokens=500)
            st.sidebar.info(completion.choices[0].message.content)
        except Exception as e: st.sidebar.error(f"⚠️ Error: {e}")

# ----------------------------------------------------------------------------------
# CUERPO PRINCIPAL DEL DASHBOARD
# ----------------------------------------------------------------------------------
st.title("🛡️ SentinelAI: Centro de Inteligencia Venezuela")
st.markdown("### 🇻🇪 Control Geográfico, Agrupamiento Avanzado y Modelos Predictivos (MLOps)")

if df is not None and not df.empty:
    st.success("📡 **INTEGRACIÓN TOTAL ACTIVA**")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hora'] = df['timestamp'].dt.hour
    df['dia_semana'] = df['timestamp'].dt.dayofweek

    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Eventos Almacenados", f"{len(df)}")
    with m2: st.metric("Incidentes Críticos", f"{len(df[df['riesgo'] == 'CRITICO'])}")
    with m3: st.metric("Nodos Activos", f"{df['estado'].nunique()}")
    with m4: st.metric("Estado Analítico", f"ML + {modelo_seleccionado.split('-')[0].upper()}")

    st.markdown("---")
    tab_monitoreo, tab_clustering, tab_prediccion = st.tabs(["📍 Monitoreo Operativo", "📊 Análisis de Clústeres (ML)", "📈 Pronóstico y Predicción (ML)"])

    with tab_monitoreo:
        fig_mapa = px.scatter_mapbox(df, lat="lat", lon="lon", color="riesgo", size="intentos_fallidos", zoom=5.5, height=500)
        fig_mapa.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_mapa, use_container_width=True)

    with tab_clustering:
        st.header("🧠 Configuración y Control de Agrupamiento No Supervisado")
        disp_col1, disp_col2 = st.columns(2)
        with disp_col1:
            st.subheader("🗺️ Distribución Espacial de Alta Frecuencia (DBSCAN)")
            if len(df) >= 3:
                X_spatial = df[['lat', 'lon']].dropna()
                dbscan = DBSCAN(eps=0.3, min_samples=2)
                df['Cluster_Espacial'] = dbscan.fit_predict(X_spatial)
                df['Nombre_Cluster'] = df['Cluster_Espacial'].apply(lambda x: "Ruido / Eventos Dispersos" if x == -1 else f"Hotspot Geográfico {x}")
                fig_spatial_disp = px.scatter(df, x="lon", y="lat", color="Nombre_Cluster", size="intentos_fallidos", title="DBSCAN (Frecuencia: Actualización en vivo)")
                st.plotly_chart(fig_spatial_disp, use_container_width=True)
        with disp_col2:
            st.subheader("🕒 Distribución Temporal de Frecuencia Semanal (K-Means)")
            if len(df) >= 3:
                X_behavior = df[['intentos_fallidos', 'dia_semana', 'hora']].dropna()
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X_behavior)
                kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
                df['ID_Perfil'] = kmeans.fit_predict(X_scaled)
                df['Perfil_Atacante'] = df['ID_Perfil'].apply(lambda x: f"Perfil Atacante {x}")
                fig_behavior_disp = px.scatter(df, x="dia_semana", y="hora", color="Perfil_Atacante", size="intentos_fallidos", title="K-Means (Ventana Dinámica)")
                st.plotly_chart(fig_behavior_disp, use_container_width=True)

    with tab_prediccion:
        st.header("🎯 Reporte de Inferencia Temporal (Vulnerabilidades)")
        if len(df) >= 8:
            try:
                df['bloque_hora'] = df['timestamp'].dt.floor('h')
                serie_temporal = df.groupby('bloque_hora').agg({'intentos_fallidos': 'sum', 'hora': 'first'}).reset_index().sort_values('bloque_hora')
                serie_temporal['intentos_anterior_hora'] = serie_temporal['intentos_fallidos'].shift(1).bfill()
                gbt = GradientBoostingRegressor(n_estimators=50, random_state=42)
                gbt.fit(serie_temporal[['intentos_anterior_hora', 'hora']], serie_temporal['intentos_fallidos'])
                ult_volumen = serie_temporal['intentos_fallidos'].iloc[-1]
                prediccion_proxima_hora = max(0, int(gbt.predict([[ult_volumen, int((serie_temporal['hora'].iloc[-1] + 1) % 24)]])[0]))

                col_m1, col_m2 = st.columns([1, 2])
                with col_m1:
                    st.metric(label="Volumen de Intentos en el Último Bloque", value=f"{int(ult_volumen)}")
                    st.metric(label="Proyección de Intentos (Próxima Hora)", value=f"🔮 {prediccion_proxima_hora}", delta=f"{int(prediccion_proxima_hora - ult_volumen)} vs bloque basal")
                with col_m2:
                    serie_temporal['Prediccion_Modelo'] = gbt.predict(serie_temporal[['intentos_anterior_hora', 'hora']])
                    fig_trend = px.line(serie_temporal, x='bloque_hora', y=['intentos_fallidos', 'Prediccion_Modelo'], title="Ajuste de Tendencia del Modelo Predictivo")
                    st.plotly_chart(fig_trend, use_container_width=True)
            except Exception as e_ml: st.error(f"Error ML: {e_ml}")

    st.markdown("---")
    st.dataframe(df[['timestamp', 'ip_origen', 'estado', 'riesgo', 'diagnostico_ia']].head(30), use_container_width=True)
else:
    st.warning("📡 Inicializando base de datos central en Supabase...")

# Recarga automática rápida de 4 segundos MIENTRAS la pestaña del navegador esté abierta
time.sleep(4)
st.rerun()
