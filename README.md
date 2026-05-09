# SentinelAI: Predictive Network Intrusion Detection System (NIDS)

![SentinelAI Banner](https://img.shields.io/badge/SentinelAI-Production--Ready-blue?style=for-the-badge&logo=python)
![ML](https://img.shields.io/badge/Algorithm-Isolation%20Forest-orange?style=for-the-badge)

**SentinelAI** es un sistema avanzado de detección de intrusiones en red que utiliza Machine Learning para identificar anomalías sin depender de reglas estáticas. El sistema analiza el comportamiento del tráfico en 4 dimensiones críticas (intentos, reputación, intensidad y variedad) para tomar decisiones autónomas de bloqueo o alerta.

---

## 📊 Arquitectura del Proyecto

El sistema está diseñado bajo una arquitectura modular para facilitar su escalabilidad:

- **`analizador_ml.py`**: El motor de IA. Implementa `Isolation Forest` para detección de anomalías.
- **`app_streamlit.py`**: Dashboard Web interactivo con analítica avanzada en tiempo real.
- **`simulador_trafico.py`**: Interfaz de terminal (CLI) para monitoreo ligero.
- **`database_manager.py`**: Capa de persistencia en SQLite con gestión de conexiones seguras.
- **`schema_seguridad.py`**: Validación de datos con Pydantic V2 para asegurar la integridad de la red.

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

## 🛠️ Guía de Inicio Rápido

### Opción A: Despliegue con Docker (Recomendado)
Ideal para entornos aislados y listos para producción.

1.  **Construir la imagen**:
    ```bash
    docker build -t sentinel-nids .
    ```
2.  **Lanzar el contenedor**:
    ```bash
    docker run -p 8501:8501 sentinel-nids
    ```
3.  **Acceso**: Abre tu navegador en [http://localhost:8501](http://localhost:8501).

### Opción B: Ejecución Local (Python)
Para desarrollo y pruebas rápidas.

1.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Iniciar el Dashboard Web**:
    ```bash
    streamlit run app_streamlit.py
    ```
3.  **Iniciar el Monitor de Terminal (Opcional)**:
    ```bash
    python simulador_trafico.py
    ```

---

## 🧪 Cómo probar el sistema

Una vez dentro del **Dashboard Web (Streamlit)**:
1. Dirígete al panel lateral izquierdo.
2. Ajusta la cantidad de eventos en el slider.
3. Haz clic en **"Lanzar Simulación"**.
4. Observa cómo las gráficas de **Distribución de Riesgos** y la **Línea de Tiempo** se actualizan automáticamente al detectar anomalías generadas por el motor de IA.

---

## 🛠️ Tecnologías Utilizadas

- **Core:** Python 3.12+
- **Machine Learning:** Scikit-Learn, NumPy
- **Visualización:** Plotly, Streamlit, Rich
- **Data & Ops:** Pydantic V2, Pandas, SQLite, Docker (uv optimized)

---

*Desarrollado para la protección proactiva de infraestructuras críticas mediante inteligencia artificial.*
