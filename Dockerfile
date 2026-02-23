# Usamos la versión COMPLETA de Python (más robusta que la slim)
FROM python:3.11

# Configuración de entorno
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 1. Instalamos solo lo mínimo indispensable (Chrome y dependencias de PDF)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    shared-mime-info \
    --no-install-recommends

# 2. Instalamos Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb \
    && apt-get clean

# 3. Directorio de trabajo
WORKDIR /app

# 4. Instalamos las librerías de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiamos el código
COPY . .

EXPOSE 8000

# Ejecutamos con reload para que veas tus cambios al guardar
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]