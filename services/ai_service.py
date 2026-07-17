"""Servicio de IA usando OpenRouter para resúmenes y recomendaciones."""

import os
from datetime import date, timedelta
from typing import Optional

import httpx
from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import engine
from models import Tarea, Examen, Materia, StatusTarea

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"


async def _call_llm(system: str, user: str) -> str:
    """Llama a OpenRouter con manejo de rate limiting y errores."""
    if not API_KEY:
        return "⚠️ OPENROUTER_API_KEY no configurada. Edita el .env"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://school-api.local",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.3,
        "max_tokens": 1024,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(BASE_URL, json=payload, headers=headers)
        if resp.status_code == 429:
            return "⚠️ Rate limit alcanzado en OpenRouter. Espera un momento y vuelve a intentar."
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


def _build_contexto_semana() -> str:
    """Recolecta datos de la semana en DB para dar contexto al LLM."""
    hoy = date.today()
    fin_semana = hoy + timedelta(days=7)

    with Session(engine) as session:
        result = session.execute(
            select(Tarea).where(
                Tarea.fecha_entrega >= hoy,
                Tarea.fecha_entrega <= fin_semana,
            ).order_by(Tarea.fecha_entrega)
        )
        tareas = result.scalars().all()

        result = session.execute(
            select(Examen).where(
                Examen.fecha >= hoy,
                Examen.fecha <= fin_semana,
            ).order_by(Examen.fecha)
        )
        examenes = result.scalars().all()

        result = session.execute(
            select(Tarea).where(
                Tarea.fecha_entrega < hoy,
                Tarea.status != StatusTarea.completada,
            )
        )
        vencidas = result.scalars().all()

        # Eager load materias
        for t in tareas:
            _ = t.materia
        for t in vencidas:
            _ = t.materia
        for e in examenes:
            _ = e.materia

    lines = ["--- CONTEXTO SEMANAL ---"]
    if vencidas:
        lines.append(f"\n🔴 Tareas VENCIDAS ({len(vencidas)}):")
        for t in vencidas:
            lines.append(f"  - {t.titulo} (venció {t.fecha_entrega}) [{t.materia.nombre}]")

    if tareas:
        lines.append(f"\n📋 Tareas de la semana ({len(tareas)}):")
        for t in tareas:
            lines.append(f"  - {t.titulo} → {t.fecha_entrega} [{t.materia.nombre}] ({t.prioridad.value})")

    if examenes:
        lines.append(f"\n📚 Exámenes próximos ({len(examenes)}):")
        for e in examenes:
            lines.append(f"  - {e.titulo} → {e.fecha} [{e.materia.nombre}]")

    return "\n".join(lines)


async def resumen_semana() -> str:
    """Genera un resumen de la semana escolar."""
    contexto = _build_contexto_semana()
    return await _call_llm(
        system="Eres un asistente escolar que ayuda al estudiante a organizar su semana. "
               "Da un resumen útil, motivador y en español. Sé concreto: menciona fechas, prioridades y riesgos.",
        user=f"Genera un resumen de mi semana escolar:\n\n{contexto}",
    )


async def prioridades_hoy() -> str:
    """Recomienda qué estudiar hoy."""
    contexto = _build_contexto_semana()
    return await _call_llm(
        system="Eres un tutor académico. Recomienda al estudiante QUÉ estudiar HOY basado en "
               "vencimientos y exámenes próximos. Prioriza lo urgente. Responde en español, máximo 5 balas.",
        user=f"¿Qué debería estudiar hoy?\n\n{contexto}",
    )


async def generar_prompt_estudio(tema: str, materia: Optional[str] = None) -> str:
    """Genera un prompt personalizado para estudiar un tema."""
    contexto = f"Materia: {materia}\n" if materia else ""
    return await _call_llm(
        system="Genera un plan de estudio personalizado en español. Incluye: objetivos, "
               "tiempo estimado, puntos clave a repasar, y 3 preguntas de práctica.",
        user=f"Necesito estudiar: {tema}\n{contexto}",
    )
