# 🛡️ SentinelAI: MLOps-Driven Network Intrusion Detection System (NIDS)

![SentinelAI Status](https://img.shields.io/badge/SentinelAI-V2.1--Production-blue?style=for-the-badge&logo=python)
![ML Engine](https://img.shields.io/badge/Engine-Isolation%20Forest%20%7C%20Llama%203-orange?style=for-the-badge)
![Telemetry Type](https://img.shields.io/badge/Telemetry-Synthetic%20%7C%20Simulated-yellow?style=for-the-badge)
![License](https://img.shields.io/badge/License-Apache%202.0-red?style=for-the-badge)

**SentinelAI** es un ecosistema de ciberseguridad agencial avanzado para la detección de anomalías y el análisis forense en red. El proyecto consta de dos interfaces complementarias: un agente de monitoreo y bloqueo de IP activo basado en terminal, y un dashboard forense web unificado en Streamlit.

---

## ⚠️ Declaración de Honestidad Técnica e Ingeniería de Datos

En línea con los más altos estándares de transparencia técnica, declaramos que:
1. **Telemetría Simulada e Híbrida:** Todo el tráfico y las métricas de red procesadas por el agente de terminal (`simulador_trafico.py`) y el alimentador (`feeder_global.py`) se generan de forma **sintética y simulada** basándose en distribuciones realistas de frecuencia de red (como la distribución de Pareto para simular ráfagas de ataques). No se utiliza tráfico de red real de producción, lo cual permite un entorno de pruebas seguro y reproducible ideal para demostraciones.
2. **Entorno Bajo Demanda y Fallback Local:** La persistencia e ingesta global se orquesta de forma híbrida. El sistema utiliza de forma nativa una base de datos local SQLite (`sentinel_logs.db`) y, opcionalmente, sincroniza en tiempo real con la nube a través de **Supabase** si las credenciales correspondientes están configuradas en el archivo `.env`. Si no hay credenciales configuradas, el sistema cae de manera segura al almacenamiento SQLite local sin interrumpir la operación.

---

## 🤖 El Agente de Análisis y Decisiones Autónomas

El núcleo inteligente del monitor local en terminal es la clase `MotorDecision` (en `analizador_ml.py`). Este componente actúa como un agente de seguridad activo autónomo utilizando un enfoque híbrido:

### 🔄 Modelo de Evaluación: Bootstrap con Transición Adaptativa
Para garantizar la viabilidad y robustez del aprendizaje automático no supervisado sin requerir un gran conjunto de datos precargados, el motor implementa un ciclo de vida dinámico:
- **Modo Bootstrap Heurístico (Muestras < 30):** Mientras el historial local (persistido en SQLite) acumule menos de $N = 30$ registros, el agente opera mediante reglas heurísticas estáticas sobre los intentos fallidos, permitiendo la recopilación segura de logs iniciales.
- **Modo ML Activo (Muestras ≥ 30):** Una vez alcanzado el umbral configurable de $N = 30$ muestras, el sistema entrena automáticamente en caliente un modelo **`sklearn.ensemble.IsolationForest`** con parámetros estables.
- **Características Multidimensionales Procesadas por el Modelo:**
  1. *Volumen:* Cantidad de intentos fallidos concurrentes.
  2. *Origen Geográfico/IP:* Los cuatro octetos de la IP de origen desglosados numéricamente.
  3. *Protocolo:* Codificación numérica determinista del protocolo de red utilizado.
  4. *Temporalidad:* Hora del día y día de la semana extraídos de la marca de tiempo de la alerta.
- **Puntuación de Riesgo Adaptativa y No Heurística:** Las puntuaciones de decisión (`decision_function` score) del modelo de Isolation Forest se mapean a las categorías estándar de riesgo usando constantes nombradas no mágicas:
  - `score < -0.15` ➡️ **RIESGO CRÍTICO** (Bloqueo inmediato de la IP y envío opcional de alertas vía Webhook externo).
  - `score < -0.05` ➡️ **RIESGO ALTO** (Restricción preventiva de ancho de banda).
  - En otro caso ➡️ **RIESGO MEDIO / BAJO** (Monitoreo activo ordinario).

---

## 🚀 Características Principales

### 📡 Sentinel Agent V2.1 (Monitor en Tiempo Real)
Motor de aislamiento activo basado en terminal que procesa telemetría de tráfico en vivo.
- **Motor de Aislamiento Activo**: Clasificación de anomalías por Isolation Forest en caliente y bloqueo de IP en tiempo real.
- **Analítica de Pareto**: Identificación visual de los agresores de mayor impacto directamente en el CLI.
- **Puntuación de Riesgo Adaptativa**: Distribución de riesgo codificada por colores (CRÍTICO, MEDIO, BAJO).

### 🧠 Dashboard Forense Potenciado por IA
Interfaz de Streamlit de alto contraste para la investigación profunda de incidentes.
- **Consultor Forense LLM**: Potenciado por **Groq Cloud (Llama 3.3-70B)** para la generación automatizada de reportes de seguridad en lenguaje natural.
- **Modelado Predictivo**: Integración con **DBSCAN y K-Means** para el agrupamiento de amenazas y predicción de tendencias.
- **Pipeline de Ingesta Global**: Almacenamiento persistente de logs y telemetría vía **Supabase** de manera opcional y con fallback local automático.

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
- **AI/ML**: Scikit-learn (Isolation Forest, DBSCAN, K-Means, Gradient Boosting Regressor), Groq Cloud (Llama 3.3-70B).
- **Backend/Data**: Supabase (PostgreSQL), SQLite (Local Fallback), Python 3.12.
- **DevOps**: Gestión del ciclo de vida MLOps y contenedores.
- **Enlace**: En el siguiente enlace puede ver la simulación en vivo e interactuar  https://sentinelai-nids-lk3vflstx3kc4dr7ujo6sa.streamlit.app/ 

---

## ⚙️ Instalación y Uso

1. **Clonar e Instalar**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Configuración del Entorno**:
   Crea un archivo `.env` con tus credenciales (opcional para el monitor local, pero requerido para el dashboard completo con IA):
   ```env
   GROQ_API_KEY=tu_clave
   SUPABASE_URL=tu_url
   SUPABASE_KEY=tu_clave
   ```
3. **Ejecutar el Agente de Monitoreo Local**:
   ```bash
   python simulador_trafico.py
   ```
4. **Ejecutar el Ingestor Global de Telemetría**:
   ```bash
   python feeder_global.py
   ```
5. **Iniciar Dashboard Forense**:
   ```bash
   streamlit run app_web.py
   ```

---

## 🗺️ Roadmap y Próximos Pasos (Capacidades Aspiracionales)

Con el fin de mantener una distinción clara entre lo implementado actualmente y la visión a futuro del proyecto, se proponen los siguientes próximos hitos de desarrollo:
- **Validación Avanzada de Firma de Paquetes:** Integración profunda con herramientas nativas de captura de paquetes (ej. `Scapy` o `pypcap`) para analizar tráfico de red real de interfaces locales (`eth0`, `wlan0`).
- **Autenticación Multifactor en Dashboard Forense:** Implementación de flujos de login seguros y control de accesos basados en roles (RBAC).
- **Automatización del Despliegue con Terraform:** Orquestación automática de la infraestructura de Supabase y servicios de contenedores en la nube (AWS/GCP).
- **Modelo de Lenguaje Local (Ollama):** Alternativa offline para el Consultor IA utilizando modelos pequeños como Phi-3 o Llama-3-8B ejecutándose localmente.

---
*Desarrollado con pasión para la defensa proactiva y honesta de infraestructuras de red.*
