import os
import sys
import random
import time
import requests
from datetime import datetime

# LIBRERÍAS DE INTERFAZ
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text

# CONFIGURACIÓN DE RUTA
base_path = os.path.dirname(os.path.abspath(__file__))
if base_path not in sys.path:
    sys.path.insert(0, base_path)

try:
    from schema_seguridad import LogEntrada
    from database_manager import inicializar_db, guardar_evento
    from analizador_ml import MotorDecision
except ImportError as e:
    print(f"❌ Error crítico: {e}")
    sys.exit(1)

console = Console()

# ==========================================================
# CONFIGURACIÓN OPCIONAL: WEBHOOK EXTERNO
# Coloca aquí tu URL de Webhook.site para recibir alertas.
# Si se deja vacío o como ejemplo, el sistema operará solo localmente.
# ==========================================================
WEBHOOK_URL = "TU_URL_AQUI" 

def enviar_alerta_webhook(decision, log):
    """Envía alerta solo si la URL ha sido configurada correctamente."""
    if not WEBHOOK_URL or "TU_URL" in WEBHOOK_URL or not WEBHOOK_URL.startswith("http"):
        return 

    payload = {
        "event": "CRITICAL_INTRUSION",
        "severity": decision.nivel_riesgo,
        "ip_source": log.ip_origen,
        "action": decision.accion_tomada,
        "reason": decision.razonamiento,
        "timestamp": log.timestamp.isoformat()
    }
    try:
        requests.post(WEBHOOK_URL, json=payload, timeout=0.8)
    except:
        pass

def generar_dashboard(eventos_log):
    totales = {"CRITICO": 0, "MEDIO": 0, "BAJO": 0}
    for e in eventos_log:
        totales[e['riesgo']] += 1
    total = sum(totales.values()) or 1
    
    def crear_barra(label, count, color):
        ancho = 20
        proc = int((count / total) * ancho)
        return f"[{color}]{label:<8} | {'█' * proc}{'░' * (ancho - proc)} | {count}[/{color}]"

    # Indicador visual del estado del Webhook
    webhook_status = "[green]ONLINE[/]" if "http" in WEBHOOK_URL.lower() and "TU_URL" not in WEBHOOK_URL else "[yellow]LOCAL_ONLY[/]"
    
    grafico = Panel(
        f"{crear_barra('CRÍTICO', totales['CRITICO'], 'bold red')}\n"
        f"{crear_barra('MEDIO', totales['MEDIO'], 'yellow')}\n"
        f"{crear_barra('BAJO', totales['BAJO'], 'green')}\n\n"
        f"Salida Externa: {webhook_status}",
        title="📊 Monitor de Amenazas IA", border_style="blue"
    )

    table = Table(expand=True)
    table.add_column("Hora", style="cyan")
    table.add_column("IP Origen", style="magenta")
    table.add_column("Riesgo", style="bold")
    table.add_column("Razón", style="italic grey70")

    for e in eventos_log[-6:]:
        estilo = "bold red" if e['riesgo'] == "CRITICO" else "yellow" if e['riesgo'] == "MEDIO" else "green"
        table.add_row(e['hora'], e['ip'], f"[{estilo}]{e['riesgo']}[/{estilo}]", e['razon'])

    return Panel(Columns([grafico, table], expand=True), title="SENTINEL AGENT LIVE")

def generar_resumen_ejecutivo(eventos_log):
    """Cierre del programa: Muestra el reporte final pase lo que pase."""
    console.clear()
    console.print(Panel("[bold green]SISTEMA SENTINEL: REPORTE ESTRATÉGICO FINAL[/bold green]", expand=False))
    
    conteo_ips = {}
    for e in eventos_log:
        if e['riesgo'] == "CRITICO":
            conteo_ips[e['ip']] = conteo_ips.get(e['ip'], 0) + 1
    
    ips_top = sorted(conteo_ips.items(), key=lambda x: x[1], reverse=True)[:5]
    table = Table(title="Top Agresores (Prioridad de Bloqueo)", title_style="bold red")
    table.add_column("Dirección IP", style="magenta")
    table.add_column("Alertas Críticas", justify="center")
    table.add_column("Impacto %", justify="right")

    total_criticos = sum(conteo_ips.values()) or 1
    for ip, cuenta in ips_top:
        impacto = (cuenta / total_criticos) * 100
        table.add_row(ip, str(cuenta), f"{impacto:.1f}%")

    resumen = Panel(
        Text.from_markup(
            f"Eventos Totales: [bold cyan]{len(eventos_log)}[/]\n"
            f"Bloqueos IA: [bold red]{total_criticos}[/]\n"
            f"Integración Webhook: {'[green]Configurada[/]' if 'http' in WEBHOOK_URL else '[yellow]Desactivada[/]'}"
        ),
        title="Métricas de Operación", border_style="cyan"
    )
    console.print(table)
    console.print(resumen)

def ejecutar_agente():
    inicializar_db()
    motor = MotorDecision()
    ips_fijas = ["192.168.1.50", "192.168.1.100", "192.168.1.150", "192.168.1.200"]
    eventos_log = []

    with Live(generar_dashboard(eventos_log), refresh_per_second=4, screen=True) as live:
        for _ in range(40):
            time.sleep(0.3)
            data = {
                "ip_origen": random.choice(ips_fijas),
                "intentos_fallidos": random.randint(1, 25),
                "protocolo": random.choice(["SSH", "HTTP", "HTTPS", "FTP"]),
                "timestamp": datetime.now()
            }
            try:
                log = LogEntrada(**data)
                decision = motor.generar_reporte(log)
                guardar_evento(log, decision.nivel_riesgo)
                
                if decision.nivel_riesgo == "CRITICO":
                    enviar_alerta_webhook(decision, log)
                
                eventos_log.append({
                    "hora": log.timestamp.strftime("%H:%M:%S"),
                    "ip": log.ip_origen,
                    "riesgo": decision.nivel_riesgo,
                    "accion": decision.accion_tomada,
                    "razon": decision.razonamiento
                })
                live.update(generar_dashboard(eventos_log))
            except Exception as e:
                # console.print(f"Error en iteración: {e}")
                continue

    generar_resumen_ejecutivo(eventos_log)

if __name__ == "__main__":
    ejecutar_agente()
