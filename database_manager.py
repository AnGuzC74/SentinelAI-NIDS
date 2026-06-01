import os
import sqlite3
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv(override=True)

class DatabaseManager:
    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL", "").strip()
        self.key = os.environ.get("SUPABASE_KEY", "").strip()
        self.client: Client = None
        if self.url and self.key:
            try:
                self.client = create_client(self.url, self.key)
            except:
                pass

    def inicializar_db(self):
        # Mantiene compatibilidad con SQLite para el Agente local
        conn = sqlite3.connect('sentinel_logs.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS logs
            (id INTEGER PRIMARY KEY AUTOINCREMENT, ip TEXT, intentos INTEGER,
             protocolo TEXT, riesgo TEXT, timestamp DATETIME)''')
        conn.commit()
        conn.close()

    def guardar_evento(self, log, riesgo, diagnostico, estado, lat, lon, embedding=None):
        # Prioriza guardado en Supabase (Cloud)
        if self.client:
            nuevo_log = {
                "ip_origen": log.ip_origen,
                "intentos_fallidos": log.intentos_fallidos,
                "protocolo": log.protocolo,
                "timestamp": log.timestamp.isoformat(),
                "riesgo": riesgo,
                "diagnostico_ia": diagnostico,
                "estado": estado,
                "lat": lat,
                "lon": lon
            }
            try:
                self.client.table("logs_globales").insert(nuevo_log).execute()
            except Exception as e:
                print(f"Error Supabase: {e}")

        # Guardado local (Fallback)
        try:
            conn = sqlite3.connect('sentinel_logs.db')
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO logs (ip, intentos, protocolo, riesgo, timestamp)
                              VALUES (?, ?, ?, ?, ?)''',
                           (log.ip_origen, log.intentos_fallidos, log.protocolo, riesgo, log.timestamp))
            conn.commit()
            conn.close()
        except:
            pass

# Instancia global para ser usada por feeder_global.py
db = DatabaseManager()

# Funciones de compatibilidad con versiones anteriores
def inicializar_db():
    db.inicializar_db()

def guardar_evento(log, riesgo):
    db.guardar_evento(log, riesgo, "Log local", "Local", 0, 0)
