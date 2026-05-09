import sqlite3
import bcrypt
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    conn = sqlite3.connect('sentinel_logs.db')
    try:
        yield conn
    finally:
        conn.close()

def inicializar_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS logs 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, ip TEXT, intentos INTEGER, 
             protocolo TEXT, riesgo TEXT, timestamp DATETIME)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS credenciales 
            (usuario TEXT PRIMARY KEY, password_hash TEXT)''')
        conn.commit()

def guardar_evento(log, riesgo):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO logs (ip, intentos, protocolo, riesgo, timestamp)
                          VALUES (?, ?, ?, ?, ?)''', 
                       (log.ip_origen, log.intentos_fallidos, log.protocolo, riesgo, log.timestamp))
        conn.commit()

def registrar_usuario(usuario, password_plano):
    salt = bcrypt.gensalt()
    pw_hash = bcrypt.hashpw(password_plano.encode('utf-8'), salt)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO credenciales (usuario, password_hash) VALUES (?, ?)", 
                           (usuario, pw_hash))
            conn.commit()
        except sqlite3.IntegrityError:
            pass 
