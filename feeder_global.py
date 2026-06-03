import time
import os
import random
from datetime import datetime
from dotenv import load_dotenv

from database_manager import db
from analizador_ml import MotorDecision
from schema_seguridad import LogEntrada

load_dotenv(override=True)

NODOS_INFRAESTRUCTURA = [
    {"estado": "Caracas, DT", "lat": 10.48, "lon": -66.89, "peso_ataques": 0.50},
    {"estado": "Maracaibo, Zulia", "lat": 10.64, "lon": -71.61, "peso_ataques": 0.30},
    {"estado": "Valencia, Carabobo", "lat": 10.16, "lon": -68.00, "peso_ataques": 0.15},
    {"estado": "Barquisimeto, Lara", "lat": 10.06, "lon": -69.34, "peso_ataques": 0.05}
]

BOTNET_REPETITIVA = ["190.202.45.110", "201.244.18.92", "186.24.195.5", "200.11.205.14"]

def simular_intentos_pareto():
    alpha = 1.5
    resultado_base = (1.0 / (random.random() ** (1.0 / alpha))) * 5
    return max(5, min(int(resultado_base), 120))

def seleccionar_nodo_ponderado():
    r = random.random()
    acumulado = 0.0
    for nodo in NODOS_INFRAESTRUCTURA:
        acumulado += nodo["peso_ataques"]
        if r <= acumulado:
            return nodo
    return NODOS_INFRAESTRUCTURA[0]

def generar_registro_industrial(motor):
    nodo_objetivo = seleccionar_nodo_ponderado()
    if random.random() > 0.3:
        ip_origen = random.choice(BOTNET_REPETITIVA)
    else:
        ip_origen = f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"

    intentos_fallidos = simular_intentos_pareto()
    protocolo = "Xmas-Scan/Exploit" if intentos_fallidos > 70 else "SSH-Bruteforce"

    log = LogEntrada(ip_origen=ip_origen, intentos_fallidos=intentos_fallidos, protocolo=protocolo, timestamp=datetime.now())
    reporte = motor.generar_reporte(log)

    db.guardar_evento(log, reporte['riesgo'], reporte['diagnostico'], nodo_objetivo['estado'], nodo_objetivo['lat'], nodo_objetivo['lon'], embedding=None)
    print(f"🛰️ [TELEMETRÍA PARETO] -> {nodo_objetivo['estado']} | IP: {ip_origen} | Intentos: {intentos_fallidos}")

def ejecutar_pipeline():
    db.inicializar_db()
    motor = MotorDecision()
    while True:
        try:
            tiempo_espera = max(5, int(random.expovariate(1.0 / 12.0)))
            generar_registro_industrial(motor)
            time.sleep(tiempo_espera)
        except KeyboardInterrupt:
            break
        except Exception as e:
            time.sleep(10)

if __name__ == "__main__":
    ejecutar_pipeline()
