# 🛡️ SentinelAI: MLOps-Driven Network Intrusion Detection System (NIDS)

![SentinelAI Status](https://img.shields.io/badge/SentinelAI-V2.1--Production-blue?style=for-the-badge&logo=python)
![ML Engine](https://img.shields.io/badge/Engine-Isolation%20Forest%20%7C%20Llama%203-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-Apache%202.0-red?style=for-the-badge)

**SentinelAI** es un ecosistema de ciberseguridad agencial avanzado, diseñado para la detección de amenazas y el análisis forense en tiempo real. Combina un motor de monitoreo de alto rendimiento en terminal con un dashboard web potenciado por IA para proporcionar una capa de defensa proactiva e inteligente.

---

## 🤖 El Agente de Análisis y Decisiones Autónomas

A diferencia de los sistemas NIDS tradicionales que solo registran eventos, **SentinelAI funciona como un Agente Autónomo**. Este componente es el núcleo del sistema y se encarga de:

1.  **Evaluación de Comportamiento (Isolation Forest):** Utiliza aprendizaje no supervisado para detectar desviaciones estadísticas en el tráfico, identificando patrones de ataque antes de que existan firmas conocidas.
2.  **Análisis Forense con LLM (Llama 3):** Interpreta los logs técnicos y genera reportes en lenguaje natural sobre la naturaleza del ataque, el nivel de riesgo y las contramedidas recomendadas.
3.  **Toma de Decisiones en Tiempo Real:** Ejecuta acciones automáticas como el bloqueo de IPs basándose en el riesgo calculado por el motor de ML.

---

## 🚀 Características Principales

### 📡 Sentinel Agent V2.1 (Monitor en Tiempo Real)
Motor de aislamiento activo basado en terminal que procesa telemetría de tráfico en vivo.
- **Motor de Aislamiento Activo**: Detección de desviaciones de protocolo y bloqueo de IP en tiempo real.
- **Analítica de Pareto**: Identificación visual de los agresores de mayor impacto directamente en el CLI.
- **Puntuación de Riesgo Adaptativa**: Distribución de riesgo codificada por colores (CRÍTICO, MEDIO, BAJO).

### 🧠 Dashboard Forense Potenciado por IA
Interfaz de Streamlit de alto contraste para la investigación profunda de incidentes.
- **Consultor Forense LLM**: Potenciado por **Groq Cloud (Llama 3)** para la generación automatizada de reportes de seguridad.
- **Modelado Predictivo**: Integración con **DBSCAN y K-Means** para el agrupamiento de amenazas y predicción de tendencias.
- **Pipeline de Ingesta Global**: Almacenamiento persistente de logs y telemetría vía **Supabase**.

---

## 📸 Technical Showcase

### 1. SentinelAI Dashboard: Monitoreo Global
Visualización unificada del estado de la red y métricas de seguridad en tiempo real.
<p align="center">
  <img src="assets/live_monitor.png" width="45%" alt="Live Monitor">
  <img src="assets/geospatial_monitoring.png" width="45%" alt="Geospatial Map">
</p>

### 2. Análisis de Clústeres y Comportamiento (ML)
Segmentación de tráfico mediante DBSCAN y K-Means para identificar Hotspots de ataque.
<p align="center">
  <img src="assets/risk_distribution.png" width="45%" alt="Cluster Analysis">
  <img src="assets/pareto_analysis.png" width="45%" alt="Pareto Analysis">
</p>

### 3. Agresores de Alto Impacto y Tabulación Forense
Identificación precisa de IPs maliciosas y volumen de intentos fallidos.
<p align="center">
  <img src="assets/aggressor_table.png" width="90%" alt="Aggressor Table">
</p>

### 4. Consultor IA y Predicción Proactiva
Análisis forense con Llama 3 y modelos predictivos para anticipar futuras vulnerabilidades.
<p align="center">
  <img src="assets/ai_consultant_ui.png" width="45%" alt="AI Forensic Agent">
  <img src="assets/ai_analysis_results.png" width="45%" alt="Predictive Analysis">
</p>

---

## 🛠️ Arquitectura y Stack

- **Frontend**: Streamlit (Dashboard), Rich/Terminal (Agent).
- **AI/ML**: Scikit-learn (Isolation Forest, DBSCAN, K-Means), Groq Cloud (Llama 3.3-70B).
- **Backend/Data**: Supabase (PostgreSQL), Python 3.11.
- **DevOps**: Gestión del ciclo de vida MLOps y contenedores.

---

## ⚙️ Instalación

1. **Clonar e Instalar**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Configuración del Entorno**:
   Crea un archivo `.env` con tus credenciales:
   ```env
   GROQ_API_KEY=tu_clave
   SUPABASE_URL=tu_url
   SUPABASE_KEY=tu_clave
   ```
3. **Ejecutar el Agente**:
   ```bash
   python simulador_trafico.py
   ```
4. **Iniciar Dashboard**:
   ```bash
   streamlit run app_web.py
   ```

---
*Desarrollado para la defensa proactiva de infraestructuras de red críticas.*
