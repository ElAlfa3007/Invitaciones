import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, insert, update
from sqlalchemy.exc import IntegrityError  # Añadido para capturar duplicados

from database import engine
from dynamic_tables import crear_tabla_evento, obtener_tabla_evento, listar_eventos
from schemas import CrearEvento, CargaInvitados, ActualizarEstado, BuscarInvitado
from auth import verificar_admin

app = FastAPI(title="Invitaciones API")

# Lee los dominios permitidos desde Render; por defecto permite localhost para desarrollo local
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_tabla_o_404(slug: str):
    tabla = obtener_tabla_evento(slug)
    if tabla is None:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return tabla


# ---------------------------------------------------------------------------
# ADMIN — requieren header X-Admin-Key
# ---------------------------------------------------------------------------

@app.post("/admin/eventos", dependencies=[Depends(verificar_admin)])
def crear_evento(datos: CrearEvento):
    columnas_extra = [c.model_dump() for c in datos.columnas_extra] if datos.columnas_extra else []
    crear_tabla_evento(datos.slug, columnas_extra)
    return {"mensaje": f"Evento '{datos.slug}' creado"}


@app.get("/admin/eventos", dependencies=[Depends(verificar_admin)])
def eventos_existentes():
    return {"eventos": listar_eventos()}


@app.post("/admin/eventos/{slug}/invitados", dependencies=[Depends(verificar_admin)])
def cargar_invitados(slug: str, datos: CargaInvitados):
    tabla = get_tabla_o_404(slug)

    columnas_insertables = [
        c.name for c in tabla.columns
        if c.name not in ("id", "estado", "fecha_registro", "fecha_actualizacion")
    ]

    filas = []
    for inv in datos.invitados:
        datos_inv = inv.model_dump()
        fila = {col: datos_inv.get(col) for col in columnas_insertables}
        filas.append(fila)

    # Bloque try/except para manejar el UniqueConstraint de PostgreSQL y SQLite
    try:
        with engine.begin() as conn:
            conn.execute(insert(tabla), filas)
    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="Error de integridad: La lista contiene invitados duplicados (mismo nombre y apellido) o ya existen en este evento."
        )

    return {"mensaje": f"{len(filas)} invitados cargados"}


@app.get("/admin/eventos/{slug}/invitados", dependencies=[Depends(verificar_admin)])
def listar_invitados(slug: str):
    tabla = get_tabla_o_404(slug)
    with engine.connect() as conn:
        filas = conn.execute(select(tabla)).mappings().all()

    resumen = {"asiste": 0, "no_asiste": 0, "pendiente": 0}
    for fila in filas:
        resumen[fila["estado"]] = resumen.get(fila["estado"], 0) + 1

    return {"resumen": resumen, "invitados": [dict(f) for f in filas]}


# ---------------------------------------------------------------------------
# PÚBLICO — usados desde la página de invitación
# ---------------------------------------------------------------------------

@app.post("/eventos/{slug}/buscar")
def buscar_invitado(slug: str, datos: BuscarInvitado):
    tabla = get_tabla_o_404(slug)
    
    # Como Pydantic ya aplicó strip() y lower() en el esquema (paso previo),
    # no necesitamos hacerlo manualmente aquí. Mantenemos ilike por máxima compatibilidad.
    with engine.connect() as conn:
        fila = conn.execute(
            select(tabla).where(
                tabla.c.nombre.ilike(datos.nombre),
                tabla.c.apellido.ilike(datos.apellido),
            )
        ).mappings().first()

    if not fila:
        raise HTTPException(
            status_code=404,
            detail="No encontramos tu invitación. Verifica nombre y apellido.",
        )
    return dict(fila)


@app.patch("/eventos/{slug}/invitados/{invitado_id}")
def actualizar_estado(slug: str, invitado_id: int, datos: ActualizarEstado):
    tabla = get_tabla_o_404(slug)
    with engine.begin() as conn:
        resultado = conn.execute(
            update(tabla).where(tabla.c.id == invitado_id).values(estado=datos.estado)
        )
        if resultado.rowcount == 0:
            raise HTTPException(status_code=404, detail="Invitado no encontrado")
    return {"mensaje": "Estado actualizado"}


@app.get("/")
def raiz():
    return {"estado": "ok", "servicio": "Invitaciones API"}