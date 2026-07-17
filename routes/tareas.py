"""CRUD de tareas con eager loading vía selectinload."""

from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from database import get_session
from models import Tarea, StatusTarea
from schemas import TareaCreate, TareaRead, TareaUpdate

router = APIRouter(prefix="/tareas", tags=["tareas"])

SessionDep = Annotated[Session, Depends(get_session)]

_BASE_OPTIONS = [selectinload(Tarea.materia)]


def _enriquecer(t: Tarea) -> TareaRead:
    return TareaRead(
        id=t.id,
        titulo=t.titulo,
        descripcion=t.descripcion,
        fecha_entrega=t.fecha_entrega,
        hora_entrega=t.hora_entrega,
        status=t.status,
        prioridad=t.prioridad,
        materia_id=t.materia_id,
        materia_nombre=t.materia.nombre if t.materia else "",
    )


@router.get("/", response_model=list[TareaRead])
async def listar_tareas(
    session: SessionDep,
    status: Optional[StatusTarea] = Query(None),
    materia_id: Optional[int] = Query(None),
    prioridad: Optional[str] = Query(None),
    vencidas: Optional[bool] = Query(False),
):
    query = select(Tarea).options(*_BASE_OPTIONS)
    if status:
        query = query.where(Tarea.status == status)
    if materia_id:
        query = query.where(Tarea.materia_id == materia_id)
    if prioridad:
        query = query.where(Tarea.prioridad == prioridad)
    if vencidas:
        query = query.where(Tarea.fecha_entrega < date.today(), Tarea.status != StatusTarea.completada)

    tareas = session.execute(query).scalars().all()
    return [_enriquecer(t) for t in tareas]


@router.get("/hoy", response_model=list[TareaRead])
async def tareas_hoy(session: SessionDep):
    hoy = date.today()
    tareas = session.execute(
        select(Tarea).options(*_BASE_OPTIONS).where(
            Tarea.fecha_entrega == hoy
        ).order_by(Tarea.hora_entrega, Tarea.prioridad)
    ).scalars().all()
    return [_enriquecer(t) for t in tareas]


@router.get("/{tarea_id}", response_model=TareaRead)
async def obtener_tarea(tarea_id: int, session: SessionDep):
    tarea = session.get(Tarea, tarea_id)
    if not tarea:
        raise HTTPException(404, detail="Tarea no encontrada")
    return _enriquecer(tarea)


@router.post("/", response_model=TareaRead, status_code=201)
async def crear_tarea(payload: TareaCreate, session: SessionDep):
    tarea = Tarea(**payload.model_dump())
    session.add(tarea)
    session.commit()
    session.refresh(tarea)
    return _enriquecer(tarea)


@router.patch("/{tarea_id}", response_model=TareaRead)
async def actualizar_tarea(tarea_id: int, payload: TareaUpdate, session: SessionDep):
    tarea = session.get(Tarea, tarea_id)
    if not tarea:
        raise HTTPException(404, detail="Tarea no encontrada")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(tarea, key, value)
    session.commit()
    session.refresh(tarea)
    return _enriquecer(tarea)


@router.delete("/{tarea_id}", status_code=204)
async def eliminar_tarea(tarea_id: int, session: SessionDep):
    tarea = session.get(Tarea, tarea_id)
    if not tarea:
        raise HTTPException(404, detail="Tarea no encontrada")
    session.delete(tarea)
    session.commit()
