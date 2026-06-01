from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class LogEntrada(BaseModel):
    ip_origen: str = Field(..., pattern=r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    intentos_fallidos: int = Field(..., ge=0)
    protocolo: str
    timestamp: datetime = Field(default_factory=datetime.now)

    @field_validator('ip_origen')
    @classmethod
    def validar_red_privada(cls, v: str) -> str:
        if not v.startswith("192.168."):
            raise ValueError(f"IP {v} fuera de la red local permitida.")
        return v

    @field_validator('protocolo')
    @classmethod
    def validar_protocolo_autorizado(cls, v: str) -> str:
        v_upper = v.upper()
        validos = ['SSH', 'HTTP', 'FTP', 'HTTPS']
        if v_upper not in validos:
            raise ValueError(f"Protocolo {v_upper} no reconocido.")
        return v_upper

class DecisionAgente(BaseModel):
    id_alerta: str
    nivel_riesgo: str
    accion_tomada: str
    razonamiento: str
