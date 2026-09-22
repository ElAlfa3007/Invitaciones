(function () {
  const cfg = window.CONFIG;
  if (!cfg) {
    console.error("Falta config.js con window.CONFIG en esta página de evento.");
    return;
  }

  // ---------------- Cuenta regresiva ----------------
  function actualizarCuentaRegresiva() {
    const el = document.getElementById("cuenta-regresiva");
    if (!el) return;

    const ahora = new Date();
    const objetivo = new Date(cfg.eventDate);
    const diff = objetivo - ahora;

    if (diff <= 0) {
      el.innerHTML = '<p style="grid-column: 1/-1;">¡Hoy es el día! 🎉</p>';
      return;
    }

    const dias = Math.floor(diff / (1000 * 60 * 60 * 24));
    const horas = Math.floor((diff / (1000 * 60 * 60)) % 24);
    const minutos = Math.floor((diff / (1000 * 60)) % 60);
    const segundos = Math.floor((diff / 1000) % 60);

    const bloque = (numero, etiqueta) => `
      <div class="bloque">
        <span class="numero">${numero}</span>
        <span class="etiqueta">${etiqueta}</span>
      </div>`;

    el.innerHTML =
      bloque(dias, "días") +
      bloque(horas, "hrs") +
      bloque(minutos, "min") +
      bloque(segundos, "seg");
  }

  actualizarCuentaRegresiva();
  setInterval(actualizarCuentaRegresiva, 1000);

  // ---------------- RSVP ----------------
  const formBusqueda = document.getElementById("form-busqueda");
  const panelBusqueda = document.getElementById("panel-busqueda");
  const panelConfirmacion = document.getElementById("panel-confirmacion");
  const mensajeBusqueda = document.getElementById("mensaje-busqueda");
  const nombreResultado = document.getElementById("nombre-resultado");
  const mensajeConfirmacion = document.getElementById("mensaje-confirmacion");

  let invitadoActual = null; // { id, nombre, apellido, estado }

  // Función para capitalizar nombres (disponible para búsqueda y confirmación)
  const formatearNombre = (str) => str.replace(/\b\w/g, c => c.toUpperCase());

  function mostrarMensaje(el, texto, tipo) {
    el.textContent = texto;
    el.className = "mensaje " + tipo;
    el.classList.remove("oculto");
  }

  function marcarBotonActivo(estado) {
    document.querySelectorAll(".boton-estado").forEach((btn) => {
      btn.classList.toggle("activo", btn.dataset.estado === estado);
    });
  }

  if (formBusqueda) {
    formBusqueda.addEventListener("submit", async (evento) => {
      evento.preventDefault();
      mensajeBusqueda.classList.add("oculto");

      const inputNombre = document.getElementById("input-nombre");
      const inputApellido = document.getElementById("input-apellido");
      const nombre = inputNombre.value.trim();
      const apellido = inputApellido.value.trim();
      const botonSubmit = formBusqueda.querySelector('button[type="submit"]');

      if (!nombre || !apellido) {
        mostrarMensaje(mensajeBusqueda, "Escribe tu nombre y apellido.", "error");
        return;
      }

      const textoOriginalBoton = botonSubmit.textContent;
      botonSubmit.disabled = true;
      botonSubmit.textContent = "Buscando... (puede tardar un momento)";

      const baseUrl = cfg.apiBase.replace(/\/$/, "");

      try {
        const resp = await fetch(`${baseUrl}/eventos/${cfg.slug}/buscar`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ nombre, apellido }),
        });

        if (!resp.ok) {
          const err = await resp.json().catch(() => ({}));
          mostrarMensaje(
            mensajeBusqueda,
            err.detail || "No encontramos tu invitación. Verifica los datos.",
            "error"
          );
          return;
        }

        invitadoActual = await resp.json();
        
        nombreResultado.textContent = `${formatearNombre(invitadoActual.nombre)} ${formatearNombre(invitadoActual.apellido)}`;
        marcarBotonActivo(invitadoActual.estado);

        panelBusqueda.classList.add("oculto");
        panelConfirmacion.classList.remove("oculto");
      } catch (e) {
        mostrarMensaje(mensajeBusqueda, "No pudimos conectar con el servidor. Revisa tu conexión e intenta de nuevo.", "error");
      } finally {
        botonSubmit.disabled = false;
        botonSubmit.textContent = textoOriginalBoton;
      }
    });
  }

  document.querySelectorAll(".boton-estado").forEach((boton) => {
    boton.addEventListener("click", async () => {
      if (!invitadoActual || boton.disabled) return;
      const estado = boton.dataset.estado;
      
      document.querySelectorAll(".boton-estado").forEach(b => b.disabled = true);

      const baseUrl = cfg.apiBase.replace(/\/$/, "");

      try {
        const resp = await fetch(
          `${baseUrl}/eventos/${cfg.slug}/invitados/${invitadoActual.id}`,
          {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ estado }),
          }
        );

        if (!resp.ok) {
          mostrarMensaje(mensajeConfirmacion, "No se pudo guardar tu respuesta. Intenta de nuevo.", "error");
          return;
        }

        marcarBotonActivo(estado);

        // Identificar si tiene pases múltiples configurados en este evento
        const nombreCompleto = `${formatearNombre(invitadoActual.nombre)} ${formatearNombre(invitadoActual.apellido)}`;
        const pases = (cfg.pasesEspeciales && cfg.pasesEspeciales[nombreCompleto]) ? cfg.pasesEspeciales[nombreCompleto] : 1;

        const textos = {
          asiste: pases > 1 ? `¡Genial! Los esperamos con ${pases} pases 🎉` : "¡Genial! Te esperamos 🎉",
          no_asiste: "Gracias por avisar, los extrañaremos.",
          pendiente: "Quedaste como pendiente, puedes confirmar cuando quieras.",
        };
        
        mostrarMensaje(mensajeConfirmacion, textos[estado] || "Respuesta guardada.", "exito");
      } catch (e) {
        mostrarMensaje(mensajeConfirmacion, "No pudimos conectar con el servidor. Intenta de nuevo.", "error");
      } finally {
        document.querySelectorAll(".boton-estado").forEach(b => b.disabled = false);
      }
    });
  });
})();