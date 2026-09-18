// Configuración de ESTE evento. Para crear una invitación nueva, copia toda
// la carpeta "eventos/cumple-octubre" con otro nombre y solo cambia esto:
window.CONFIG = {
  // Cuando despliegues el backend en Render, cambia esto por esa URL,
  // ej: "https://invitaciones-api.onrender.com"
  apiBase: "http://localhost:8000",

  // Debe ser el mismo slug con el que creaste el evento en el backend
  // (POST /admin/eventos)
  slug: "cumple-octubre",

  // Fecha y hora del evento, formato ISO (usada por la cuenta regresiva)
  eventDate: "2026-10-24T19:00:00",
};
