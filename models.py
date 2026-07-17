"""Modelos SQLAlchemy para school-api."""

from datetime import date, datetime, time
from sqlalchemy import Column, Integer, String, Float, Date, Time, Enum as SAEnum, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, relationship
import enum


class Base(DeclarativeBase):
    pass


class StatusTarea(str, enum.Enum):
    pendiente = "pendiente"
    completada = "completada"
    en_progreso = "en_progreso"


class Prioridad(str, enum.Enum):
    baja = "baja"
    media = "media"
    alta = "alta"
    urgente = "urgente"


# ─── Materia ────────────────────────────────────────────────────────────────


class Materia(Base):
    __tablename__ = "materia"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(120), nullable=False, index=True)
    profesor = Column(String(120), default="")
    color = Column(String(7), default="#3b82f6")
    horario = Column(String(255), default="")
    semestre = Column(String(20), default="2026-2")

    tareas = relationship("Tarea", back_populates="materia", cascade="all, delete-orphan")
    examenes = relationship("Examen", back_populates="materia", cascade="all, delete-orphan")


# ─── Tarea ──────────────────────────────────────────────────────────────────


class Tarea(Base):
    __tablename__ = "tarea"

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text, default="")
    fecha_entrega = Column(Date, nullable=False)
    hora_entrega = Column(Time, nullable=True)
    status = Column(SAEnum(StatusTarea), default=StatusTarea.pendiente)
    prioridad = Column(SAEnum(Prioridad), default=Prioridad.media)
    materia_id = Column(Integer, ForeignKey("materia.id"), nullable=False)

    materia = relationship("Materia", back_populates="tareas")


# ─── Examen ─────────────────────────────────────────────────────────────────


class Examen(Base):
    __tablename__ = "examen"

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(255), nullable=False)
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=True)
    temas = Column(Text, default="")
    peso = Column(Float, default=1.0)
    ubicacion = Column(String(255), default="")
    materia_id = Column(Integer, ForeignKey("materia.id"), nullable=False)

    materia = relationship("Materia", back_populates="examenes")
