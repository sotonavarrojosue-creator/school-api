"""CRUD de examenes con eager loading vía selectinload."""

from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from database import get_session
from models import Examen
from schemas import ExamenCreate, ExamenRead, ExamenUpdate

router = APIRouter(prefix="/examenes", tags=["examenes"])

SessionDep = Annotated[Session, Depends(get_session)]

_BASE_OPTIONS = [selectinload(Examen.materia)]


def _enriquecer(e: Examen) -> ExamenRead:
    return ExamenRead(
        id=e.id,
        titulo=e.titulo,
        fecha=e.fecha,
        hora=e.hora,
        temas=e.temas,
        peso=e.peso,
        ubicacion=e.ubicacion,
        materia_id=e.materia_id,
        materia_nombre=e.materia.nombre if e.materia else "",
    )


@router.get("/", response_model=list[ExamenRead])
async def listar_examenes(
    session: SessionDep,
    materia_id: Optional[int] = Query(None),
    proximos: Optional[bool] = Query(False),
):
    query = select(Examen).options(*_BASE_OPTIONS)
    if materia_id:
        query = query.where(Examen.materia_id == materia_id)
    if proximos:
        query = query.where(Examen.fecha >= date.today())
    query = query.order_by(Examen.fecha)

    examenes = session.execute(query).scalars().all()
    return [_enriquecer(e) for e in examenes]


@router.get("/proximos", response_model=list[ExamenRead])
async def proximos_examenes(session: SessionDep):
    examenes = session.execute(
        select(Examen).options(*_BASE_OPTIONS).where(
            Examen.fecha >= date.today()
        ).order_by(Examen.fecha).limit(10)
    ).scalars().all()
    return [_enriquecer(e) for e in examenes]


@router.get("/{examen_id}", response_model=ExamenRead)
async def obtener_examen(examen_id: int, session: SessionDep):
    examen = session.get(Examen, examen_id)
    if not examen:
        raise HTTPException(404, detail="Examen no encontrado")
    return _enriquecer(examen)


@router.post("/", response_model=ExamenRead, status_code=201)
async def crear_examen(payload: ExamenCreate, session: SessionDep):
    examen = Examen(**payload.model_dump())
    session.add(examen)
    session.commit()
    session.refresh(examen)
    return _enriquecer(examen)


@router.patch("/{examen_id}", response_model=ExamenRead)
async def actualizar_examen(examen_id: int, payload: ExamenUpdate, session: SessionDep):
    examen = session.get(Examen, examen_id)
    if not examen:
        raise HTTPException(404, detail="Examen no encontrado")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(examen, key, value)
    session.commit()
    session.refresh(examen)
    return _enriquecer(examen)


@router.delete("/{examen_id}", status_code=204)
async def eliminar_examen(examen_id: int, session: SessionDep):
    examen = session.get(Examen, examen_id)
    if not examen:
        raise HTTPException(404, detail="Examen no encontrado")
    session.delete(examen)
    session.commit()
