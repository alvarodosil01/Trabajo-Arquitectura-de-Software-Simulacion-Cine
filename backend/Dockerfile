# Imagen del backend del cine (FastAPI + SQLite).
# Construir desde la raíz del repositorio: docker compose build

FROM python:3.12-slim

# Evita ficheros .pyc y muestra los logs al momento
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_URL=sqlite:////app/data/cine.db

WORKDIR /app

# Primero las dependencias, para aprovechar la caché de capas de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Después el código de la aplicación
COPY app/ app/
COPY cine/ cine/

# Usuario sin privilegios: el contenedor no se ejecuta como root
RUN useradd --create-home --uid 1000 cine \
    && mkdir -p /app/data \
    && chown cine:cine /app/data
USER cine

# La base SQLite vive en un volumen para sobrevivir a la sustitución del contenedor
VOLUME ["/app/data"]

# Documenta el puerto; se publica al ejecutar con -p o desde docker compose
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
