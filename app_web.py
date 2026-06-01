import streamlit as st
import pandas as pd
import numpy as np
import os
import time
import random
from datetime import datetime, timedelta
from supabase import create_client, Client
from dotenv import load_dotenv
import plotly.express as px
from groq import Groq
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingRegressor

# ----------------------------------------------------------------------------------
# PARCHE DE RUTAS PARA ENTORNO CLOUD (IMPORTACIONES LOCALES)
# ----------------------------------------------------------------------------------
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager import db
from analizador_ml import MotorDecision
from schema_seguridad import LogEntrada
# ----------------------------------------------------------------------------------

# Cargar variables de entorno
load_dotenv(override=True)
st.set_page_config(page_title="SentinelAI VZLA Pro", layout="wide", page_icon="🛡️")

# Inicialización de APIs y Conexiones Cloud
url_supabase = os.environ.get("SUPABASE_URL", "").strip()
key_supabase = os.environ.get("SUPABASE_KEY", "").strip()
API_GROQ = os.environ.get("GROQ_API_KEY", "").strip()
client_groq = Groq(api_key=API_GROQ) if API_GROQ else None

# Estilos CSS de Alta Visibilidad y Contraste Profesional
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

# Parámetros de simulación geográfica
NODOS_INFRAESTRUCTURA = [
    {"estado": "Caracas, DT", "lat": 10.48, "lon": -66.89, "peso_ataques": 0.50},
    {"estado": "Maracaibo, Zulia", "lat": 10.64, "lon": -71.61, "peso_ataques": 0.30},
    {"estado": "Valencia, Carabobo", "lat": 10.16, "lon": -68.00, "peso_ataques": 0.15},
    {"estado": "Barquisimeto, Lara", "lat": 10.06, "lon": -69.34, "peso_ataques": 0.05}
]
BOTNET_REPETITIVA = ["190.202.45.110", "201.244.18.92", "186.24.195.5", "200.11.205.14"]

def generar_datos_precargados_mock():
    """Genera instantáneamente un lote estático de 25 registros para visualización inmediata"""
    registros = []
    base_time = datetime.now()
    for i in range(25):
        nodo = random.choices(NODOS_INFRAESTRUCTURA, weights=[n["peso_ataques"] for n in NODOS_INFRAESTRUCTURA])[0]
        ip = random.choice(BOTNET_REPETITIVA) if random.random() > 0.4 else f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
        intentos = random.randint(10, 110)
        protocolo = "Xmas-Scan/Exploit" if intentos > 65 else "SSH-Bruteforce"
        riesgo = "CRITICO" if intentos > 60 else ("ALTO" if intentos > 30 else "MEDIO")
        ts = (base_time - timedelta(minutes=i*12)).isoformat()

        registros.append({
            "ip_origen": ip, "intentos_fallidos": intentos, "protocolo": protocolo,
            "timestamp": ts, "riesgo": riesgo, "estado": nodo["estado"],
            "lat": nodo["lat"], "lon": nodo["lon"],
            "diagnostico_ia": f"[PRECARGADO] Mitigación exitosa contra {protocolo}. Volumen detectado: {intentos} pps."
        })
    return pd.DataFrame(registros)

def auto_inyectar_un_log_vivo(supabase_client):
    """Inyecta un log dinámico nuevo cada vez que la página recarga solita"""
    nodo = random.choices(NODOS_INFRAESTRUCTURA, weights=[n["peso_ataques"] for n in NODOS_INFRAESTRUCTURA])[0]
    ip = random.choice(BOTNET_REPETITIVA) if random.random() > 0.3 else f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
    intentos = max(5, min(int((1.0 / (random.random() ** (1.0 / 1.5))) * 5), 120))
    protocolo = "Xmas-Scan/Exploit" if intentos > 70 else "SSH-Bruteforce"
    riesgo = "CRITICO" if intentos > 60 else ("ALTO" if intentos > 30 else "MEDIO")
    diagnostico = f"[VIVO CLOUD] Intrusión en tiempo real por {protocolo}. Registrados {intentos} intentos concurrentes."

    nuevo_log = {
        "ip_origen": ip, "intentos_fallidos": intentos, "protocolo": protocolo,
        "timestamp": datetime.now().isoformat(), "riesgo": riesgo, "diagnostico_ia": diagnostico,
        "estado": nodo["estado"], "lat": nodo["lat"], "lon": nodo["lon"]
    }
    try: supabase_client.table("logs_globales").insert(nuevo_log).execute()
    except: pass

def orquestar_pipeline_datos():
    df_base = generar_datos_precargados_mock()
    if not url_supabase or not key_supabase:
        return df_base
    try:
        supabase: Client = create_client(url_supabase, key_supabase)
        auto_inyectar_un_log_vivo(supabase)
        response = supabase.table("logs_globales").select("*").order("timestamp", desc=True).limit(100).execute()
        df_real = pd.DataFrame(response.data)

        if not df_real.empty:
            df_unificado = pd.concat([df_real, df_base], ignore_index=True)
            return df_unificado
        return df_base
    except:
        return df_base

# Carga inmediata de datos
df = orquestar_pipeline_datos()

# ----------------------------------------------------------------------------------
# INTERFAZ SIDEBAR: AGENTE FORENSE IA
# ----------------------------------------------------------------------------------
st.sidebar.title("🤖 Consultor de Incidentes IA (Groq Cloud)")
modelo_seleccionado = st.sidebar.selectbox("Escoge el motor de IA:", ["llama-3.3-70b-versatile", "llama3-8b-8192"])
pregunta = st.sidebar.text_input("Escribe tu consulta de seguridad:")

if pregunta and client_groq and df is not None and not df.empty:
    with st.sidebar.spinner("Procesando en Groq Cloud..."):
        try:
            contexto_logs = ""
            for index, fila in df.head(15).iterrows():
                contexto_logs += f"- IP: {fila['ip_origen']} | Ubicación: {fila['estado']} | Riesgo: {fila['riesgo']} | Reporte Técnico: {fila['diagnostico_ia']}\n"
            prompt_completo = f"Eres un auditor forense experto en ciberseguridad. Responde basándote en estos logs:\n{contexto_logs}\nPregunta: {pregunta}"
            completion = client_groq.chat.completions.create(model=modelo_seleccionado, messages=[{"role": "user", "content": prompt_completo}], temperature=0.2, max_tokens=400)
            st.sidebar.info(completion.choices[0].message.content)
        except Exception as e: st.sidebar.error(f"⚠️ Error de Groq: {e}")

# ----------------------------------------------------------------------------------
# CUERPO PRINCIPAL DEL PANEL VISUAL
# ----------------------------------------------------------------------------------
st.title("🛡️ SentinelAI: Centro de Inteligencia Venezuela")
st.markdown("### 🇻🇪 Control Geográfico, Agrupamiento Avanzado y Modelos Predictivos (MLOps)")

if df is not None and not df.empty:
    st.success("📡 **ENTORNO BAJO DEMANDA ACTIVO (DATOS PRECARGADOS INSTANTÁNEOS)**")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hora'] = df['timestamp'].dt.hour
    df['dia_semana'] = df['timestamp'].dt.dayofweek

    # Métricas de Alto Contraste
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Eventos Procesados", f"{len(df)}")
    with m2: st.metric("Incidentes Críticos", f"{len(df[df['riesgo'] == 'CRITICO'])}")
    with m3: st.metric("Nodos Activos", f"{df['estado'].nunique()}")
    with m4: st.metric("Estado Analítico", f"PRODUCCIÓN + {modelo_seleccionado.split('-')[0].upper()}")

    st.markdown("---")
    tab_monitoreo, tab_clustering, tab_prediccion = st.tabs(["📍 Monitoreo Operativo", "📊 Análisis de Clústeres (ML)", "📈 Pronóstico y Predicción (ML)"])

    with tab_monitoreo:
        fig_mapa = px.scatter_mapbox(df, lat="lat", lon="lon", color="riesgo", size="intentos_fallidos", zoom=5.2, height=480)
        fig_mapa.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_mapa, use_container_width=True)

    with tab_clustering:
        st.header("🧠 Agrupamiento Analítico No Supervisado")
        disp_col1, disp_col2 = st.columns(2)
        with disp_col1:
            st.subheader("🗺️ Segmentación Espacial de Ataques (DBSCAN)")
            if len(df) >= 3:
                X_spatial = df[['lat', 'lon']].dropna()
                dbscan = DBSCAN(eps=0.4, min_samples=2)
                df['Cluster_Espacial'] = dbscan.fit_predict(X_spatial)
                df['Nombre_Cluster'] = df['Cluster_Espacial'].apply(lambda x: "Eventos Dispersos (Ruido)" if x == -1 else f"Hotspot Crítico Geográfico {x}")
                fig_spatial_disp = px.scatter(df, x="lon", y="lat", color="Nombre_Cluster", size="intentos_fallidos", title="Clasificación por Densidad de Coordenadas")
                st.plotly_chart(fig_spatial_disp, use_container_width=True)
        with disp_col2:
            st.subheader("🕒 Perfilamiento de Comportamiento Temporal (K-Means)")
            if len(df) >= 3:
                X_behavior = df[['intentos_fallidos', 'dia_semana', 'hora']].dropna()
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X_behavior)
                kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
                df['ID_Perfil'] = kmeans.fit_predict(X_scaled)
                df['Perfil_Atacante'] = df['ID_Perfil'].apply(lambda x: f"Patrón Operativo de Botnet {x}")
                fig_behavior_disp = px.scatter(df, x="dia_semana", y="hora", color="Perfil_Atacante", size="intentos_fallidos", title="Agrupamiento de Ataques por Ventana de Tiempo")
                st.plotly_chart(fig_behavior_disp, use_container_width=True)

    with tab_prediccion:
        st.header("🎯 Inferencia de Regresión Temporal Avanzada")
        if len(df) >= 5:
            try:
                df['bloque_hora'] = df['timestamp'].dt.floor('h')
                serie_temporal = df.groupby('bloque_hora').agg({'intentos_fallidos': 'sum', 'hora': 'first'}).reset_index().sort_values('bloque_hora')
                serie_temporal['intentos_anterior_hora'] = serie_temporal['intentos_fallidos'].shift(1).bfill()

                gbt = GradientBoostingRegressor(n_estimators=30, random_state=42)
                gbt.fit(serie_temporal[['intentos_anterior_hora', 'hora']], serie_temporal['intentos_fallidos'])
                ult_volumen = serie_temporal['intentos_fallidos'].iloc[-1]
                prediccion_proxima_hora = max(0, int(gbt.predict([[ult_volumen, int((serie_temporal['hora'].iloc[-1] + 1) % 24)]])[0]))

                col_m1, col_m2 = st.columns([1, 2])
                with col_m1:
                    st.metric(label="Volumen Detectado (Último Bloque)", value=f"{int(ult_volumen)}")
                    st.metric(label="Pronóstico Analítico (Próxima Hora)", value=f"🔮 {prediccion_proxima_hora}", delta=f"{int(prediccion_proxima_hora - ult_volumen)} vs histórico")
                with col_m2:
                    serie_temporal['Prediccion_Modelo'] = gbt.predict(serie_temporal[['intentos_anterior_hora', 'hora']])
                    fig_trend = px.line(serie_temporal, x='bloque_hora', y=['intentos_fallidos', 'Prediccion_Modelo'], title="Curva de Ajuste Predictivo - Gradient Boosting")
                    st.plotly_chart(fig_trend, use_container_width=True)
            except Exception as e_ml: st.error(f"Inferencia en cola de procesamiento... {e_ml}")

    st.markdown("---")
    st.dataframe(df[['timestamp', 'ip_origen', 'estado', 'riesgo', 'diagnostico_ia']].head(25), use_container_width=True)
else:
    st.warning("⚠️ Inicializando el entorno analítico central...")

# Refresco de alta frecuencia: recarga cada 5 segundos mientras la pestaña web esté abierta
time.sleep(5)
st.rerun()
