"""CRUD de materias con eager loading."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from database import get_session
from models import Materia
from schemas import MateriaCreate, MateriaRead

router = APIRouter(prefix="/materias", tags=["materias"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/", response_model=list[MateriaRead])
async def listar_materias(session: SessionDep):
    materias = session.execute(select(Materia)).scalars().all()
    return materias


@router.get("/{materia_id}", response_model=MateriaRead)
async def obtener_materia(materia_id: int, session: SessionDep):
    materia = session.get(Materia, materia_id)
    if not materia:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Materia no encontrada")
    return materia


@router.post("/", response_model=MateriaRead, status_code=status.HTTP_201_CREATED)
async def crear_materia(payload: MateriaCreate, session: SessionDep):
    materia = Materia(**payload.model_dump())
    session.add(materia)
    session.commit()
    session.refresh(materia)
    return materia


@router.put("/{materia_id}", response_model=MateriaRead)
async def actualizar_materia(materia_id: int, payload: MateriaCreate, session: SessionDep):
    materia = session.get(Materia, materia_id)
    if not materia:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Materia no encontrada")
    for key, value in payload.model_dump().items():
        setattr(materia, key, value)
    session.commit()
    session.refresh(materia)
    return materia


@router.delete("/{materia_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_materia(materia_id: int, session: SessionDep):
    materia = session.get(Materia, materia_id)
    if not materia:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Materia no encontrada")
    session.delete(materia)
    session.commit()
