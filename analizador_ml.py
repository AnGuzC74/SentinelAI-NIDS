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
        try:
            conn = sqlite3.connect('sentinel_logs.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM logs WHERE ip = ? AND riesgo = 'CRITICO'", (ip,))
            repu = cursor.fetchone()[0]
            hace_5 = (datetime.now() - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("SELECT COUNT(*) FROM logs WHERE ip = ? AND timestamp > ?", (ip, hace_5))
            inte = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT protocolo) FROM logs WHERE ip = ? AND timestamp > ?", (ip, hace_5))
            variedad = cursor.fetchone()[0]
            conn.close()
            return repu, inte, variedad
        except Exception:
            return 0, 0, 0

    def generar_reporte(self, log: LogEntrada) -> DecisionAgente:
        repu, inte, variedad = self.consultar_contexto(log.ip_origen)
        vector = np.array([[log.intentos_fallidos, repu, inte, variedad]])
        es_anomalia = self.modelo.predict(vector)[0]

        riesgo = "BAJO"
        razon = "Patrón validado por Isolation Forest."

        if es_anomalia == -1 or log.intentos_fallidos > 15:
            riesgo = "CRITICO"
            razon = f"ANOMALÍA: Escaneo/Fuerza Bruta (Variedad: {variedad}, Int: {inte})"
        elif log.intentos_fallidos > 6 or variedad > 1:
            riesgo = "MEDIO"
            razon = "Comportamiento inusual detectado."

        acciones = {"CRITICO": "BLOQUEAR_IP", "MEDIO": "ALERTAR", "BAJO": "LOG_ONLY"}
        return DecisionAgente(
            id_alerta=f"ML-{log.timestamp.strftime('%S%f')}",
            nivel_riesgo=riesgo,
            accion_tomada=acciones[riesgo],
            razonamiento=razon
        )
