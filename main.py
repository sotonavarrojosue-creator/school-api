"""school-api — API Personal de Tareas Escolares.

FastAPI + SQLModel + SQLite + Obsidian Sync + IA.
"""

import os
from contextlib import asynccontextmanager
from typing import Annotated

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routes import materias, tareas, examenes
from services import ai_service, obsidian_sync

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="school-api",
    description="API personal de tareas escolares con sincronización Obsidian e IA",
    version="0.1.0",
    lifespan=lifespan,
)

# ─── CORS ────────────────────────────────────────────────────────────────────

origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ─────────────────────────────────────────────────────────────────

app.include_router(materias.router)
app.include_router(tareas.router)
app.include_router(examenes.router)


# ─── Endpoints IA ────────────────────────────────────────────────────────────


@app.get("/ai/resumen-semana")
async def resumen_semana():
    """Resumen semanal generado por IA."""
    texto = await ai_service.resumen_semana()
    return {"resumen": texto}


@app.get("/ai/prioridades")
async def prioridades_hoy():
    """Recomendación de qué estudiar hoy."""
    texto = await ai_service.prioridades_hoy()
    return {"recomendacion": texto}


@app.post("/ai/estudio")
async def plan_estudio(tema: str, materia: str = ""):
    """Genera plan de estudio para un tema específico."""
    texto = await ai_service.generar_prompt_estudio(tema, materia or None)
    return {"plan": texto}


# ─── Endpoints Sync ──────────────────────────────────────────────────────────


@app.post("/sync/importar")
async def sync_importar():
    """Importa notas .md del vault → DB."""
    stats = obsidian_sync.importar_notas()
    return {"status": "ok", "stats": stats}


@app.post("/sync/exportar")
async def sync_exportar():
    """Exporta DB → archivos .md en el vault."""
    stats = obsidian_sync.exportar_db()
    return {"status": "ok", "stats": stats}


# ─── Health ──────────────────────────────────────────────────────────────────


@app.get("/health")
async def health():
    return {"status": "ok", "app": "school-api"}


# ─── Entrypoint ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
