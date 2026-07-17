"""Pydantic V2 schemas para school-api."""

from datetime import date, time
from typing import Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict

from models import StatusTarea, Prioridad


# ─── Materia ────────────────────────────────────────────────────────────────


class MateriaBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str
    profesor: str = ""
    color: str = "#3b82f6"
    horario: str = ""
    semestre: str = "2026-2"


class MateriaCreate(MateriaBase):
    pass


class MateriaRead(MateriaBase):
    id: int


# ─── Tarea ──────────────────────────────────────────────────────────────────


class TareaBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    titulo: str
    descripcion: str = ""
    fecha_entrega: date
    hora_entrega: Optional[time] = None
    status: StatusTarea = StatusTarea.pendiente
    prioridad: Prioridad = Prioridad.media
    materia_id: int


class TareaCreate(TareaBase):
    pass


class TareaRead(TareaBase):
    id: int
    materia_nombre: str = ""


class TareaUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_entrega: Optional[date] = None
    hora_entrega: Optional[time] = None
    status: Optional[StatusTarea] = None
    prioridad: Optional[Prioridad] = None
    materia_id: Optional[int] = None


# ─── Examen ─────────────────────────────────────────────────────────────────


class ExamenBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    titulo: str
    fecha: date
    hora: Optional[time] = None
    temas: str = ""
    peso: float = 1.0
    ubicacion: str = ""
    materia_id: int

    @field_validator("peso")
    @classmethod
    def validar_peso(cls, v: float) -> float:
        if v < 0 or v > 100:
            raise ValueError("Peso debe estar entre 0 y 100")
        return v


class ExamenCreate(ExamenBase):
    pass


class ExamenRead(ExamenBase):
    id: int
    materia_nombre: str = ""


class ExamenUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    titulo: Optional[str] = None
    fecha: Optional[date] = None
    hora: Optional[time] = None
    temas: Optional[str] = None
    peso: Optional[float] = None
    ubicacion: Optional[str] = None
    materia_id: Optional[int] = None
