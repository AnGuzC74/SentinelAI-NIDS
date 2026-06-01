import numpy as np
from datetime import datetime
from schema_seguridad import LogEntrada

class MotorDecision:
    def __init__(self):
        pass

    def generar_reporte(self, log: LogEntrada):
        # Lógica simplificada para velocidad de demostración (Acelerada para Reclutadores)
        if log.intentos_fallidos > 60:
            riesgo = "CRITICO"
            razon = f"ANOMALÍA: Volumen extremo de intentos ({log.intentos_fallidos})."
        elif log.intentos_fallidos > 30:
            riesgo = "ALTO"
            razon = "Comportamiento sospechoso de fuerza bruta."
        else:
            riesgo = "MEDIO"
            razon = "Actividad monitorizada."

        return {
            "riesgo": riesgo,
            "diagnostico": razon
        }
