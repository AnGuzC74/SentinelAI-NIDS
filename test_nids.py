import unittest
from datetime import datetime
from schema_seguridad import LogEntrada
from analizador_ml import MotorDecision, ReporteMotor, N_MIN_MUESTRAS

class TestSentinelNIDS(unittest.TestCase):
    def setUp(self):
        # Crear un motor de decisión limpio para cada test
        self.motor = MotorDecision()
        # Asegurarse de que el historial de logs empiece vacío para evitar efectos secundarios
        self.motor.historial_logs = []
        self.motor.modelo = None

    def test_reporte_motor_dict_subscripting(self):
        """
        Verifica la compatibilidad de ReporteMotor con acceso tanto de atributo
        como de diccionario (subscripting) requerido por feeder_global.py y app_web.py.
        """
        reporte = ReporteMotor(
            id_alerta="ALT-TEST1234",
            nivel_riesgo="CRITICO",
            accion_tomada="BLOQUEO_IP_AUTOMATICO",
            razonamiento="Prueba de compatibilidad"
        )
        # Acceso por atributos
        self.assertEqual(reporte.nivel_riesgo, "CRITICO")
        self.assertEqual(reporte.razonamiento, "Prueba de compatibilidad")
        self.assertEqual(reporte.accion_tomada, "BLOQUEO_IP_AUTOMATICO")

        # Acceso por diccionario (backward compatibility)
        self.assertEqual(reporte["riesgo"], "CRITICO")
        self.assertEqual(reporte["diagnostico"], "Prueba de compatibilidad")
        self.assertEqual(reporte["accion"], "BLOQUEO_IP_AUTOMATICO")
        self.assertEqual(reporte["nivel_riesgo"], "CRITICO")
        self.assertEqual(reporte["razonamiento"], "Prueba de compatibilidad")

    def test_modo_bootstrap_riesgo_medio(self):
        """
        Verifica que en el modo Bootstrap (muestras < 30) un log normal
        se clasifique correctamente como riesgo MEDIO.
        """
        log = LogEntrada(
            ip_origen="192.168.1.10",
            intentos_fallidos=5,
            protocolo="SSH",
            timestamp=datetime.now()
        )
        reporte = self.motor.generar_reporte(log)
        self.assertEqual(reporte.nivel_riesgo, "MEDIO")
        self.assertEqual(reporte.accion_tomada, "MONITOREO_ACTIVO")
        self.assertIn("MODO BOOTSTRAP", reporte.razonamiento)

    def test_modo_bootstrap_riesgo_alto(self):
        """
        Verifica que en el modo Bootstrap (muestras < 30) un log sospechoso
        de fuerza bruta se clasifique como riesgo ALTO.
        """
        log = LogEntrada(
            ip_origen="192.168.1.11",
            intentos_fallidos=45,
            protocolo="SSH",
            timestamp=datetime.now()
        )
        reporte = self.motor.generar_reporte(log)
        self.assertEqual(reporte.nivel_riesgo, "ALTO")
        self.assertEqual(reporte.accion_tomada, "RESTRICCION_ANCHO_BANDA")
        self.assertIn("MODO BOOTSTRAP", reporte.razonamiento)

    def test_modo_bootstrap_riesgo_critico(self):
        """
        Verifica que en el modo Bootstrap (muestras < 30) un log extremadamente
        elevado se clasifique como riesgo CRITICO.
        """
        log = LogEntrada(
            ip_origen="192.168.1.12",
            intentos_fallidos=75,
            protocolo="SSH",
            timestamp=datetime.now()
        )
        reporte = self.motor.generar_reporte(log)
        self.assertEqual(reporte.nivel_riesgo, "CRITICO")
        self.assertEqual(reporte.accion_tomada, "BLOQUEO_IP_AUTOMATICO")
        self.assertIn("MODO BOOTSTRAP", reporte.razonamiento)

    def test_transicion_bootstrap_a_isolation_forest(self):
        """
        Verifica el ciclo de vida adaptativo: el motor pasa de usar reglas simples (Bootstrap)
        a usar Isolation Forest de sklearn una vez alcanzado el umbral de 30 muestras.
        """
        # 1. Alimentar con 29 muestras (Modo Bootstrap activo)
        for i in range(29):
            log = LogEntrada(
                ip_origen=f"192.168.1.{10+i}",
                intentos_fallidos=10,  # Patrón de tráfico normal homogéneo
                protocolo="SSH",
                timestamp=datetime.now()
            )
            reporte = self.motor.generar_reporte(log)
            # Asegurarse de que cada una de las primeras 29 esté bajo el Bootstrap
            self.assertIn("MODO BOOTSTRAP", reporte.razonamiento)
            self.assertIsNone(self.motor.modelo)

        # 2. Agregar la muestra número 30 (Alcanza el umbral N=30, entrena y cambia a Isolation Forest)
        log_30 = LogEntrada(
            ip_origen="192.168.1.50",
            intentos_fallidos=12,
            protocolo="SSH",
            timestamp=datetime.now()
        )
        reporte_30 = self.motor.generar_reporte(log_30)

        # Debe haber entrenado el modelo Isolation Forest
        self.assertIsNotNone(self.motor.modelo)
        self.assertIn("ML-IsolationForest", reporte_30.razonamiento)

        # 3. Evaluar un comportamiento altamente anómalo que rompa con la homogeneidad anterior
        log_anomalo = LogEntrada(
            ip_origen="10.0.0.99",
            intentos_fallidos=150,  # Enorme volumen comparado con los anteriores de ~10
            protocolo="XMAS-SCAN",
            timestamp=datetime.now()
        )
        reporte_anomalo = self.motor.generar_reporte(log_anomalo)

        # El Isolation Forest debería clasificar esta ráfaga desviada como una anomalía
        # (al tener un score de decisión negativo muy bajo debido a la desviación de features)
        self.assertIn("ML-IsolationForest", reporte_anomalo.razonamiento)
        # Comprobar si el riesgo subió debido a la anomalía calculada por ML
        self.assertIn(reporte_anomalo.nivel_riesgo, ["ALTO", "CRITICO"])

if __name__ == "__main__":
    unittest.main()
