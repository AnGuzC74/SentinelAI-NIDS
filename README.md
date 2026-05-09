# SentinelAI: Predictive Network Intrusion Detection System (NIDS)

![SentinelAI Banner](https://img.shields.io/badge/SentinelAI-Production--Ready-blue?style=for-the-badge&logo=python)
![ML](https://img.shields.io/badge/Algorithm-Isolation%20Forest-orange?style=for-the-badge)

**SentinelAI** es un sistema avanzado de detección de intrusiones en red que utiliza Machine Learning para identificar anomalías sin depender de reglas estáticas. El sistema analiza el comportamiento del tráfico en 4 dimensiones críticas para tomar decisiones autónomas de bloqueo o alerta.

---

## 🚀 Características Principales

- **IA-Driven**: Motor basado en Scikit-Learn (`Isolation Forest`).
- **Dashboard Dual**: Interfaz de terminal enriquecida (`Rich`) y Dashboard Web interactivo (`Streamlit`).
- **Validación Estricta**: Modelado de datos con `Pydantic`.
- **Persistencia Segura**: Registro de logs en SQLite y gestión de credenciales con `bcrypt`.
- **Despliegue Rápido**: Dockerfile optimizado con `uv`.

---

## 📊 Arquitectura del Sistema

El sistema se divide en módulos independientes:

1.  **`analizador_ml.py`**: El cerebro del NIDS. Evalúa el riesgo comparando el tráfico actual con el histórico.
2.  **`app_streamlit.py`**: Interfaz visual con gráficas en tiempo real de protocolos, riesgos y línea de tiempo.
3.  **`simulador_trafico.py`**: Simulador de bajo nivel para pruebas en terminal.
4.  **`database_manager.py`**: Manejo de `sentinel_logs.db`.

---

## 📸 Galería de la Interfaz

<p align="center">
  <img src="assets/Captura de pantalla 2026-05-07 223349.png" width="45%" alt="Terminal Dashboard">
  <img src="assets/Captura de pantalla 2026-05-07 223358.png" width="45%" alt="Analytics">
</p>
<p align="center">
  <img src="assets/Captura de pantalla 2026-05-07 010141.png" width="90%" alt="Full Dashboard View">
</p>

---

## 🛠️ Instalación y Uso

### Con Docker (Recomendado)

```bash
docker build -t sentinel-ai-nids .
docker run -p 8501:8501 sentinel-ai-nids
```
*Accede a http://localhost:8501 para ver el dashboard web.*

### Instalación Manual

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Iniciar Dashboard Web:
   ```bash
   streamlit run app_streamlit.py
   ```
3. O iniciar modo Terminal:
   ```bash
   python simulador_trafico.py
   ```

---

## 🛠️ Tecnologías

- **Lenguaje:** Python 3.12+
- **IA:** Scikit-Learn (Isolation Forest), NumPy
- **Web/UI:** Streamlit, Plotly, Rich
- **Data:** Pydantic, Pandas, SQLite
- **Seguridad:** Bcrypt
- **DevOps:** Docker, uv

---

*Desarrollado para la protección proactiva de infraestructuras críticas.*
