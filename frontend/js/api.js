// Cliente de la API REST del cine. Todas las llamadas pasan por request().

const BASE = (window.CINE_API_BASE ?? '/api').replace(/\/$/, '');

export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

const CAMPOS = {
  nombre: 'Nombre', duracion: 'Duración', genero: 'Género', fecha: 'Fecha',
  precio: 'Precio', email: 'Email', butacas: 'Butacas', pelicula_id: 'Película',
  sala_id: 'Sala', sesion_id: 'Sesión',
};

// FastAPI devuelve `detail` como texto (errores de negocio) o como lista (422).
function mensajeDe(detail, status) {
  if (typeof detail === 'string' && detail) return detail;
  if (Array.isArray(detail) && detail.length) {
    return detail
      .map((e) => {
        const campo = CAMPOS[e.loc?.[e.loc.length - 1]] ?? e.loc?.slice(1).join('.') ?? '';
        const msg = String(e.msg ?? 'valor no válido').replace(/^Value error, /, '');
        return campo ? `${campo}: ${msg}` : msg;
      })
      .join(' · ');
  }
  if (status === 503) return 'La base de datos no está disponible. Inténtalo de nuevo en unos segundos.';
  if (status === 404) return 'No se ha encontrado lo que buscabas.';
  return `Error inesperado del servidor (${status}).`;
}

async function request(path, { method = 'GET', body, params } = {}) {
  let url = BASE + path;
  if (params) {
    const qs = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== ''),
    ).toString();
    if (qs) url += `?${qs}`;
  }

  let res;
  try {
    res = await fetch(url, {
      method,
      headers: body !== undefined ? { 'Content-Type': 'application/json' } : undefined,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError(0, 'No se puede conectar con el servidor. Comprueba que el backend está en marcha.');
  }

  if (res.status === 204) return null;

  let data = null;
  try {
    data = await res.json();
  } catch {
    /* respuesta sin JSON */
  }
  if (!res.ok) throw new ApiError(res.status, mensajeDe(data?.detail, res.status));
  return data;
}

const enc = encodeURIComponent;

export const api = {
  // Películas
  peliculas: () => request('/peliculas'),
  pelicula: (id) => request(`/peliculas/${enc(id)}`),
  crearPelicula: (data) => request('/peliculas', { method: 'POST', body: data }),
  actualizarPelicula: (id, data) => request(`/peliculas/${enc(id)}`, { method: 'PUT', body: data }),
  eliminarPelicula: (id) => request(`/peliculas/${enc(id)}`, { method: 'DELETE' }),

  // Salas
  salas: () => request('/salas'),

  // Sesiones
  sesiones: (peliculaId) => request('/sesiones', { params: { pelicula_id: peliculaId } }),
  sesion: (id) => request(`/sesiones/${enc(id)}`),
  crearSesion: (data) => request('/sesiones', { method: 'POST', body: data }),
  actualizarSesion: (id, data) => request(`/sesiones/${enc(id)}`, { method: 'PUT', body: data }),
  eliminarSesion: (id) => request(`/sesiones/${enc(id)}`, { method: 'DELETE' }),
  butacas: (id) => request(`/sesiones/${enc(id)}/butacas`),

  // Reservas
  crearReserva: (data) => request('/reservas', { method: 'POST', body: data }),
  reservasPorEmail: (email) => request('/reservas', { params: { email } }),
  reserva: (id) => request(`/reservas/${enc(id)}`),
};

// Carga de una vez todo lo que casi todas las pantallas necesitan.
export async function loadCatalog() {
  const [peliculas, salas, sesiones] = await Promise.all([api.peliculas(), api.salas(), api.sesiones()]);
  return {
    peliculas,
    salas,
    sesiones,
    peliculaPorId: new Map(peliculas.map((p) => [p.id, p])),
    salaPorId: new Map(salas.map((s) => [s.id, s])),
  };
}
