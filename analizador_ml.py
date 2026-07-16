import numpy as np
import os
import sqlite3
import uuid
from datetime import datetime
from sklearn.ensemble import IsolationForest
from schema_seguridad import LogEntrada, DecisionAgente

# CONSTANTES DE CONFIGURACIÓN DEL MODELO ML (Evitando números mágicos)
N_MIN_MUESTRAS = 30
UMBRAL_RIESGO_CRITICO = -0.15
UMBRAL_RIESGO_ALTO = -0.05

class ReporteMotor(DecisionAgente):
    """
    Subclase de DecisionAgente que soporta acceso por corchetes (subscripting)
    para mantener total compatibilidad con app_web.py y feeder_global.py.
    """
    def __getitem__(self, item):
        mapping = {
            "riesgo": "nivel_riesgo",
            "diagnostico": "razonamiento",
            "accion": "accion_tomada",
            "nivel_riesgo": "nivel_riesgo",
            "razonamiento": "razonamiento",
            "accion_tomada": "accion_tomada"
        }
        attr = mapping.get(item, item)
        if hasattr(self, attr):
            return getattr(self, attr)
        raise KeyError(item)

def extraer_features(log: LogEntrada) -> list:
    """
    Extrae características numéricas multidimensionales deterministas a partir de un LogEntrada.
    """
    # 1. Intentos fallidos (frecuencia/volumen)
    intentos = float(log.intentos_fallidos)

    # 2. IP Origen desglosada en sus 4 octetos numéricos
    try:
        octetos = [float(x) for x in log.ip_origen.split(".")]
        if len(octetos) != 4:
            octetos = [0.0, 0.0, 0.0, 0.0]
    except Exception:
        octetos = [0.0, 0.0, 0.0, 0.0]

    # 3. Protocolo codificado de forma estática y determinista
    protocolos_comunes = {
        "SSH": 1.0,
        "HTTP": 2.0,
        "HTTPS": 3.0,
        "FTP": 4.0,
        "XMAS-SCAN/EXPLOIT": 5.0,
        "XMAS-SCAN": 5.0,
        "EXPLOIT": 5.0
    }
    proto_upper = log.protocolo.upper()
    proto_val = protocolos_comunes.get(proto_upper, float(hash(proto_upper) % 10 + 6))

    # 4. Características temporales derivadas del timestamp
    hora = float(log.timestamp.hour)
    dia_semana = float(log.timestamp.weekday())

    return [intentos, octetos[0], octetos[1], octetos[2], octetos[3], proto_val, hora, dia_semana]

class MotorDecision:
    def __init__(self):
        self.historial_logs = []
        self.modelo = None
        self._cargar_datos_historicos()

    def _cargar_datos_historicos(self):
        """
        Carga datos históricos desde la base de datos local SQLite para inicializar
        el búfer de entrenamiento si el archivo existe y contiene registros.
        """
        try:
            conn = sqlite3.connect('sentinel_logs.db')
            cursor = conn.cursor()
            cursor.execute("SELECT ip, intentos, protocolo, timestamp FROM logs ORDER BY id DESC LIMIT 1000")
            rows = cursor.fetchall()
            conn.close()

            for row in reversed(rows):
                ip, intentos, protocolo, ts_str = row
                try:
                    ts = datetime.fromisoformat(ts_str)
                except ValueError:
                    try:
                        ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S.%f")
                    except ValueError:
                        ts = datetime.now()

                log = LogEntrada(ip_origen=ip, intentos_fallidos=intentos, protocolo=protocolo, timestamp=ts)
                self.historial_logs.append(log)
        except Exception:
            pass

    def entrenar_modelo(self):
        """
        Entrena el modelo de Isolation Forest usando los datos numéricos extraídos
        de todo el historial acumulado en el búfer.
        """
        if len(self.historial_logs) < N_MIN_MUESTRAS:
            return False

        try:
            X = [extraer_features(log) for log in self.historial_logs]
            X = np.array(X)
            # Entrenamos Isolation Forest con parámetros estables para detectar anomalías de tráfico
            self.modelo = IsolationForest(n_estimators=100, random_state=42, contamination='auto')
            self.modelo.fit(X)
            return True
        except Exception:
            self.modelo = None
            return False

    def generar_reporte(self, log: LogEntrada) -> ReporteMotor:
        """
        Evalúa el log entrante utilizando el modelo Isolation Forest (si está entrenado)
        o cayendo al modo Bootstrap heurístico si no hay suficientes muestras aún.
        """
        # Añadir log actual al historial para futuros entrenamientos
        self.historial_logs.append(log)

        # Intentar entrenar/actualizar el modelo si tenemos suficientes datos
        modelo_activo = False
        if len(self.historial_logs) >= N_MIN_MUESTRAS:
            modelo_activo = self.entrenar_modelo()

        id_alerta = f"ALT-{uuid.uuid4().hex[:8].upper()}"

        if modelo_activo and self.modelo is not None:
            # --- EVALUACIÓN UTILIZANDO ISOLATION FOREST ---
            features_actual = np.array([extraer_features(log)])
            score = float(self.modelo.decision_function(features_actual)[0])

            # Clasificación de riesgo basada en umbrales configurados
            if score < UMBRAL_RIESGO_CRITICO:
                riesgo = "CRITICO"
                accion = "BLOQUEO_IP_AUTOMATICO"
                razon = f"ANOMALÍA CRÍTICA (ML-IsolationForest score: {score:.4f}): Comportamiento de tráfico extremadamente anómalo detectado."
            elif score < UMBRAL_RIESGO_ALTO:
                riesgo = "ALTO"
                accion = "RESTRICCION_ANCHO_BANDA"
                razon = f"ANOMALÍA ALTA (ML-IsolationForest score: {score:.4f}): Patrón sospechoso desviado del comportamiento estándar."
            else:
                riesgo = "MEDIO"
                accion = "MONITOREO_ACTIVO"
                razon = f"Tránsito estadísticamente normal (ML-IsolationForest score: {score:.4f})."
        else:
            # --- EVALUACIÓN EN MODO BOOTSTRAP (REGLAS TRANSICIONALES HEURÍSTICAS) ---
            progreso_bootstrap = f"[{len(self.historial_logs)}/{N_MIN_MUESTRAS}]"
            if log.intentos_fallidos > 60:
                riesgo = "CRITICO"
                accion = "BLOQUEO_IP_AUTOMATICO"
                razon = f"MODO BOOTSTRAP {progreso_bootstrap}: Volumen crítico de intentos ({log.intentos_fallidos})."
            elif log.intentos_fallidos > 30:
                riesgo = "ALTO"
                accion = "RESTRICCION_ANCHO_BANDA"
                razon = f"MODO BOOTSTRAP {progreso_bootstrap}: Sospecha de fuerza bruta por intentos fallidos elevados."
            else:
                riesgo = "MEDIO"
                accion = "MONITOREO_ACTIVO"
                razon = f"MODO BOOTSTRAP {progreso_bootstrap}: Tránsito normal bajo supervisión estándar."

        return ReporteMotor(
            id_alerta=id_alerta,
            nivel_riesgo=riesgo,
            accion_tomada=accion,
            razonamiento=razon
        )
