import sqlite3
import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import datetime, timedelta
from schema_seguridad import LogEntrada, DecisionAgente

class MotorDecision:
    def __init__(self):
        self.modelo = IsolationForest(contamination=0.05, random_state=42)
        self._entrenar_con_contexto()

    def _entrenar_con_contexto(self):
        # [Intentos, Reputación, Intensidad, Variedad_Protocolos]
        normal = np.random.randint(0, 4, size=(100, 4))
        ataques = np.random.randint(10, 25, size=(10, 4))
        X = np.vstack([normal, ataques])
        self.modelo.fit(X)

    def consultar_contexto(self, ip):
        # En el modo industrial, el contexto local puede no estar disponible
        return 0, 0, 0

    def generar_reporte(self, log: LogEntrada):
        # Adaptado para retornar el formato esperado por el feeder global
        repu, inte, variedad = self.consultar_contexto(log.ip_origen)
        vector = np.array([[log.intentos_fallidos, repu, inte, variedad]])

        try:
            es_anomalia = self.modelo.predict(vector)[0]
        except:
            es_anomalia = 1

        riesgo = "BAJO"
        razon = "Patrón validado por Isolation Forest."

        if es_anomalia == -1 or log.intentos_fallidos > 60:
            riesgo = "CRITICO"
            razon = f"ANOMALÍA DETECTADA: Volumen extremo de intentos ({log.intentos_fallidos})."
        elif log.intentos_fallidos > 30:
            riesgo = "ALTO"
            razon = "Comportamiento sospechoso de fuerza bruta."
        elif log.intentos_fallidos > 15:
            riesgo = "MEDIO"
            razon = "Actividad por encima del umbral normal."

        return {
            "riesgo": riesgo,
            "diagnostico": razon
        }
