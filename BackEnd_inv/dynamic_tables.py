from typing import Optional
from sqlalchemy import Table, Column, Integer, String, Text, DateTime, UniqueConstraint, func, inspect
from .database import metadata, engine

TIPOS_EXTRA = {
    "texto": String(255),
    "numero": Integer,
    "largo": Text,
}

def nombre_tabla(slug: str) -> str:
    limpio = slug.strip().lower().replace("-", "_").replace(" ", "_")
    return f"invitados_{limpio}"

def crear_tabla_evento(slug: str, columnas_extra: Optional[list] = None) -> Table:
    nombre = nombre_tabla(slug)
    if nombre in metadata.tables:
        return metadata.tables[nombre]

    columnas = [
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("nombre", String(120), nullable=False),
        Column("apellido", String(120), nullable=False),
        Column("estado", String(20), nullable=False, server_default="pendiente"),
        Column("fecha_registro", DateTime, server_default=func.now()),
        Column("fecha_actualizacion", DateTime, server_default=func.now(), onupdate=func.now()),
        # Evita invitados duplicados por evento
        UniqueConstraint("nombre", "apellido", name=f"uq_{nombre}_nombre_apellido")
    ]

    for extra in columnas_extra or []:
        tipo = TIPOS_EXTRA.get(extra.get("tipo", "texto"), String(255))
        columnas.append(Column(extra["nombre"], tipo, nullable=True))

    tabla = Table(nombre, metadata, *columnas, extend_existing=True)
    metadata.create_all(engine, tables=[tabla])
    return tabla


def obtener_tabla_evento(slug: str) -> Optional[Table]:
    """Devuelve la tabla del evento, reflejándola desde la BD si no está en memoria."""
    nombre = nombre_tabla(slug)
    if nombre in metadata.tables:
        return metadata.tables[nombre]

    inspector = inspect(engine)
    if nombre in inspector.get_table_names():
        metadata.reflect(bind=engine, only=[nombre])
        return metadata.tables[nombre]

    return None


def listar_eventos() -> list:
    """Devuelve los slugs de todos los eventos existentes en la BD."""
    inspector = inspect(engine)
    return [
        t.replace("invitados_", "", 1)
        for t in inspector.get_table_names()
        if t.startswith("invitados_")
    ]
