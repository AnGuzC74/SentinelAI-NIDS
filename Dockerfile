# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Instalar dependencias del sistema necesarias (curl para healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requerimientos primero para cachear capas
COPY requirements.txt .

# Instalación de dependencias usando uv
RUN uv pip install --system --no-cache -r requirements.txt

# Copiar resto del código
COPY . .

# Exponer puerto para Streamlit
EXPOSE 8501

# Salud del contenedor
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Lanzar Dashboard Web
ENTRYPOINT ["streamlit", "run", "app_streamlit.py", "--server.port=8501", "--server.address=0.0.0.0"]
