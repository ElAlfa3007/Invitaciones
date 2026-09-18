import os
from fastapi import Header, HTTPException, status

# Sin valor por defecto seguro. Si no se configura en Render, nadie entra.
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")

def verificar_admin(x_admin_key: str = Header(...)):
    # Validamos que la llave exista en el entorno y coincida
    if not ADMIN_API_KEY or x_admin_key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado",
        )