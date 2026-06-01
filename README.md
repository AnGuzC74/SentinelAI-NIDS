# 🛡️ SentinelAI: Predictive Network Intrusion Detection System (NIDS)

![SentinelAI Status](https://img.shields.io/badge/SentinelAI-Production--Ready-blue?style=for-the-badge&logo=python)
![ML Engine](https://img.shields.io/badge/Algorithm-Isolation%20Forest-orange?style=for-the-badge)

**SentinelAI** es un sistema avanzado de detección de intrusiones en red que utiliza Machine Learning para identificar anomalías sin depender de reglas estáticas. El sistema analiza el comportamiento del tráfico en 4 dimensiones críticas (intentos, reputación, intensidad y variedad) para tomar decisiones autónomas de bloqueo o alerta.

### 🚀 Ver en Vivo (V1.0)
Puedes ver la versión estable del modelo en acción en el siguiente dashboard:
👉 **[SentinelAI Live Demo](https://sentinelai-nids-lk3vflstx3kc4dr7ujo6sa.streamlit.app/)**

---

## 📈 Evolución del Proyecto

SentinelAI ha evolucionado de un monitor de tráfico local a un ecosistema agencial de ciberseguridad.

### Fase 1: Cimientos y Detección Local (Rama `main`)
*   **Enfoque**: Monitoreo de red local y visualización básica.
*   **Motor**: Isolation Forest configurado para anomalías estadísticas simples.
*   **Arquitectura**: Persistencia en SQLite y dashboard local de Streamlit.
*   **Estado**: Estable y operativo para auditorías rápidas.

### Fase 2: Inteligencia Agencial y MLOps (Rama `desarrollo-frontend-ml`)
*   **Enfoque**: Análisis forense asistido por IA y escalabilidad en la nube.
*   **Innovaciones**:
    *   **Consultor IA (Llama 3)**: Integración con Groq Cloud para interpretar ataques en lenguaje natural.
    *   **Pipeline Cloud**: Ingesta global de logs mediante Supabase.
    *   **Clustering Avanzado**: Implementación de DBSCAN y K-Means para identificar Hotspots de ataque geográfico.
    *   **Inferencia Predictiva**: Modelos de Gradient Boosting para anticipar volúmenes de ataque en la próxima hora.
*   **Visualización**: Dashboard de alto contraste optimizado para Centros de Operaciones de Seguridad (SOC).

---

## 📊 Arquitectura (V1.0)

- **`analizador_ml.py`**: Motor de detección basado en Isolation Forest.
- **`app_streamlit.py`**: Dashboard Web interactivo.
- **`simulador_trafico.py`**: Interfaz de terminal para monitoreo en tiempo real.
- **`database_manager.py`**: Gestión de logs en SQLite.

---

## 📸 Galería (V1.0)

<p align="center">
  <img src="assets/Captura de pantalla 2026-05-07 223349.png" width="45%" alt="Terminal Dashboard">
  <img src="assets/Captura de pantalla 2026-05-07 223358.png" width="45%" alt="Analytics">
</p>

---

## 🛠️ Tecnologías

- **Core:** Python 3.12+
- **IA/ML:** Scikit-Learn, Isolation Forest.
- **Ops:** Docker, Pydantic V2, SQLite.

---
*Para ver las capacidades avanzadas de IA, cambia a la rama `desarrollo-frontend-ml`.*
