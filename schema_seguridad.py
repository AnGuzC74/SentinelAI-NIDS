from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional

class LogEntrada(BaseModel):
    ip_origen: str = Field(..., pattern=r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    intentos_fallidos: int = Field(..., ge=0)
    protocolo: str
    timestamp: datetime = Field(default_factory=datetime.now)

    @field_validator('protocolo')
    @classmethod
    def validar_protocolo_autorizado(cls, v: str) -> str:
        # Permitimos más protocolos para el modo industrial
        return v.upper()

class DecisionAgente(BaseModel):
    id_alerta: str
    nivel_riesgo: str
    accion_tomada: str
    razonamiento: str
