# Imagen del frontend del cine: ficheros estáticos servidos por nginx.
# nginx también reenvía /api/ al backend (ver nginx.conf), por eso no hace falta CORS.
# Construir desde la raíz del repositorio: docker compose build

FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html config.js /usr/share/nginx/html/
COPY css/ /usr/share/nginx/html/css/
COPY js/ /usr/share/nginx/html/js/

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -q -O /dev/null http://127.0.0.1/ || exit 1
