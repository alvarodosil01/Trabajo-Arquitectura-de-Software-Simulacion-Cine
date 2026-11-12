// Configuración del frontend. Se puede cambiar sin recompilar nada.
// "/api" es la ruta por la que nginx (Docker) o serve.py (local) reenvían las
// peticiones al backend FastAPI, así el navegador no necesita CORS.
// Para apuntar directamente a otro servidor: window.CINE_API_BASE = 'http://127.0.0.1:8000';
window.CINE_API_BASE = '/api';
