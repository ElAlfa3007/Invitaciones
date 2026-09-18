# Invitaciones API

Backend en FastAPI para invitaciones digitales con RSVP. Cada evento tiene su
propia tabla de invitados (mismos campos base, ampliable por evento), y los
datos completos solo son visibles con la clave de admin.

## Cómo funciona

- **Admin** crea un evento y carga la lista de invitados (nombre + apellido,
  más columnas extra opcionales como `alergias`).
- **Invitado** entra a la página del evento, escribe su nombre y apellido
  para confirmar quién es, y ve/actualiza su estado: `pendiente`, `asiste`
  o `no_asiste`.
- **Admin** puede ver en cualquier momento el resumen (cuántos asisten, no
  asisten o siguen pendientes) y la lista completa.

## Instalación local

```bash
pip install -r requirements.txt
cp .env.example .env   # y edita ADMIN_API_KEY con una clave real
uvicorn app.main:app --reload
```

La API queda en `http://127.0.0.1:8000`. Documentación interactiva
automática en `http://127.0.0.1:8000/docs`.

Por defecto usa SQLite (`invitaciones.db`, cero configuración). Para usar
Postgres, define `DATABASE_URL` en `.env`:
```
DATABASE_URL=postgresql://usuario:clave@host:5432/nombre_bd
```

## Endpoints

### Admin (requieren header `X-Admin-Key: <tu-clave>`)

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/admin/eventos` | Crea un evento nuevo (`slug`, `columnas_extra` opcional) |
| GET | `/admin/eventos` | Lista los slugs de eventos existentes |
| POST | `/admin/eventos/{slug}/invitados` | Carga la lista de invitados |
| GET | `/admin/eventos/{slug}/invitados` | Lista completa + resumen de estados |

### Público (usados desde la página de invitación)

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/eventos/{slug}/buscar` | Busca al invitado por `nombre` + `apellido` |
| PATCH | `/eventos/{slug}/invitados/{id}` | Actualiza el `estado` del invitado |

### Ejemplo: crear un evento con campo extra

```bash
curl -X POST https://tu-api.onrender.com/admin/eventos \
  -H "X-Admin-Key: tu-clave" -H "Content-Type: application/json" \
  -d '{"slug": "cumple-octubre", "columnas_extra": [{"nombre": "alergias", "tipo": "texto"}]}'
```

### Ejemplo: flujo del invitado

```bash
# 1. Busca su invitación
curl -X POST https://tu-api.onrender.com/eventos/cumple-octubre/buscar \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Juan", "apellido": "Perez"}'
# -> devuelve {"id": 1, "estado": "pendiente", ...}

# 2. Confirma su estado
curl -X PATCH https://tu-api.onrender.com/eventos/cumple-octubre/invitados/1 \
  -H "Content-Type: application/json" \
  -d '{"estado": "asiste"}'
```

## Desplegar (Render, gratis)

1. Sube esta carpeta a un repo de GitHub (puede ser privado).
2. En Render → New → Web Service → conecta el repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. En "Environment", agrega `ADMIN_API_KEY` (y `DATABASE_URL` si usas Postgres).
6. En `app/main.py`, cambia `allow_origins=["*"]` por el dominio real de tu
   GitHub Pages (ej. `["https://tuusuario.github.io"]`) antes de ir a producción.

## Próximos pasos

- Conectar el frontend (GitHub Pages) a estos endpoints.
- Opcional: endpoint de "sugerencias" que devuelva coincidencias parciales
  por nombre, para cuando dos invitados compartan el mismo nombre.
