"""Sincronización school-api ↔ Obsidian vault.

- Importar notas .md con frontmatter → DB
- Exportar DB → archivos .md en el vault
"""

import os
import re
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import engine
from models import Materia, Tarea, Examen

load_dotenv()

# ─── Config ─────────────────────────────────────────────────────────────────

VAULT_PATH = Path(os.getenv("SYNC_VAULT_PATH", "../OBSIIDIAN/Aaron_segundo_cerebro/Escuela"))
NOTES_DIR = VAULT_PATH / "notas"
EXPORT_DIR = VAULT_PATH / "export"

# ─── Frontmatter parsing ────────────────────────────────────────────────────

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)


def parse_frontmatter(content: str) -> Optional[dict]:
    """Extrae frontmatter YAML de un string markdown."""
    m = FRONTMATTER_RE.match(content)
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return None


def build_frontmatter(data: dict) -> str:
    """Genera frontmatter YAML como string."""
    return f"---\n{yaml.dump(data, allow_unicode=True, default_flow_style=False).strip()}\n---\n"


# ─── Import ─────────────────────────────────────────────────────────────────


def importar_notas() -> dict:
    """Lee notas .md del vault y crea/actualiza registros en DB."""
    stats = {"materias": 0, "tareas": 0, "examenes": 0, "errores": 0}

    if not NOTES_DIR.exists() or not NOTES_DIR.is_dir():
        return stats

    with Session(engine) as session:
        for md_file in sorted(NOTES_DIR.glob("*.md")):
            try:
                content = md_file.read_text(encoding="utf-8")
                fm = parse_frontmatter(content)
                if not fm:
                    continue

                tipo = fm.get("tipo", "")
                if tipo == "materia":
                    _import_materia(session, fm, stats)
                elif tipo == "tarea":
                    _import_tarea(session, fm, stats)
                elif tipo == "examen":
                    _import_examen(session, fm, stats)
            except Exception:
                stats["errores"] += 1

        session.commit()

    return stats


def _import_materia(session: Session, fm: dict, stats: dict):
    nombre = fm.get("nombre", "")
    if not nombre:
        return
    existing = session.execute(select(Materia).where(Materia.nombre == nombre)).scalar_one_or_none()
    if existing:
        for k in ("profesor", "color", "horario", "semestre"):
            if k in fm:
                setattr(existing, k, fm[k])
    else:
        session.add(Materia(
            nombre=nombre,
            profesor=fm.get("profesor", ""),
            color=fm.get("color", "#3b82f6"),
            horario=fm.get("horario", ""),
            semestre=fm.get("semestre", "2026-2"),
        ))
    stats["materias"] += 1


def _import_tarea(session: Session, fm: dict, stats: dict):
    materia = session.execute(
        select(Materia).where(Materia.nombre == fm.get("materia", ""))
    ).scalar_one_or_none()
    if not materia:
        return
    session.add(Tarea(
        titulo=fm.get("titulo", "Sin título"),
        descripcion=fm.get("descripcion", ""),
        fecha_entrega=_parse_date(fm.get("fecha_entrega")),
        status=fm.get("status", "pendiente"),
        prioridad=fm.get("prioridad", "media"),
        materia_id=materia.id,
    ))
    stats["tareas"] += 1


def _import_examen(session: Session, fm: dict, stats: dict):
    materia = session.execute(
        select(Materia).where(Materia.nombre == fm.get("materia", ""))
    ).scalar_one_or_none()
    if not materia:
        return
    session.add(Examen(
        titulo=fm.get("titulo", "Sin título"),
        fecha=_parse_date(fm.get("fecha")),
        temas=fm.get("temas", ""),
        peso=float(fm.get("peso", 1.0)),
        ubicacion=fm.get("ubicacion", ""),
        materia_id=materia.id,
    ))
    stats["examenes"] += 1


# ─── Export ──────────────────────────────────────────────────────────────────


def exportar_db() -> dict:
    """Exporta toda la DB a archivos .md organizados en el vault."""
    stats = {"materias": 0, "tareas": 0, "examenes": 0}

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    with Session(engine) as session:
        # Materias
        materias_dir = EXPORT_DIR / "materias"
        materias_dir.mkdir(exist_ok=True)
        for m in session.execute(select(Materia)).scalars().all():
            content = build_frontmatter({
                "tipo": "materia",
                "nombre": m.nombre,
                "profesor": m.profesor,
                "color": m.color,
                "horario": m.horario,
                "semestre": m.semestre,
            })
            content += f"\n# {m.nombre}\n\nMateria del semestre {m.semestre}.\n"
            _safe_write(materias_dir / f"{_slugify(m.nombre)}.md", content)
            stats["materias"] += 1

        # Tareas
        tareas_dir = EXPORT_DIR / "tareas"
        tareas_dir.mkdir(exist_ok=True)
        for t in session.execute(select(Tarea)).scalars().all():
            _ = t.materia  # eager load
            content = build_frontmatter({
                "tipo": "tarea",
                "titulo": t.titulo,
                "materia": t.materia.nombre if t.materia else "",
                "fecha_entrega": t.fecha_entrega.isoformat(),
                "status": t.status.value if hasattr(t.status, 'value') else t.status,
                "prioridad": t.prioridad.value if hasattr(t.prioridad, 'value') else t.prioridad,
            })
            content += f"\n# {t.titulo}\n\n{t.descripcion}\n"
            _safe_write(tareas_dir / f"{_slugify(t.titulo)}.md", content)
            stats["tareas"] += 1

        # Examenes
        examenes_dir = EXPORT_DIR / "examenes"
        examenes_dir.mkdir(exist_ok=True)
        for e in session.execute(select(Examen)).scalars().all():
            _ = e.materia
            content = build_frontmatter({
                "tipo": "examen",
                "titulo": e.titulo,
                "materia": e.materia.nombre if e.materia else "",
                "fecha": e.fecha.isoformat(),
                "temas": e.temas,
                "peso": e.peso,
            })
            content += f"\n# {e.titulo}\n\n**Fecha:** {e.fecha}\n\n**Temas:** {e.temas}\n"
            _safe_write(examenes_dir / f"{_slugify(e.titulo)}.md", content)
            stats["examenes"] += 1

    return stats


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _parse_date(val) -> date:
    if isinstance(val, date):
        return val
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, str):
        try:
            return date.fromisoformat(val)
        except ValueError:
            return date.today()
    return date.today()


def _slugify(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9\u00f1\u00d1\-_ ]", "", text).strip().replace(" ", "-").lower()[:80]


def _safe_write(path: Path, content: str):
    path.write_text(content, encoding="utf-8")
