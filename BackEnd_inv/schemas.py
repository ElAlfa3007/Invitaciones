from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict, field_validator

class ColumnaExtra(BaseModel):
    nombre: str
    tipo: Literal["texto", "numero", "largo"] = "texto"

class CrearEvento(BaseModel):
    slug: str
    columnas_extra: Optional[List[ColumnaExtra]] = None

class Invitado(BaseModel):
    model_config = ConfigDict(extra="allow")
    nombre: str
    apellido: str

    @field_validator('nombre', 'apellido')
    @classmethod
    def normalizar_texto(cls, v: str) -> str:
        return v.strip().lower()

class CargaInvitados(BaseModel):
    invitados: List[Invitado]

class ActualizarEstado(BaseModel):
    estado: Literal["pendiente", "asiste", "no_asiste"]

class BuscarInvitado(BaseModel):
    nombre: str
    apellido: str

    @field_validator('nombre', 'apellido')
    @classmethod
    def normalizar_texto(cls, v: str) -> str:
        return v.strip().lower()