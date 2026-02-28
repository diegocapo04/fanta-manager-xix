# Usa immagine Python leggera
FROM python:3.10-slim

# Evita che Python scriva file .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Imposta directory di lavoro
WORKDIR /app

# Installa dipendenze di sistema necessarie per compilare alcune lib Python
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia prima i requirements per sfruttare la cache di Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il resto del codice
COPY . .

# Espone la porta di Streamlit
EXPOSE 8501

# Healthcheck per assicurarsi che l'app sia viva
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Comando di avvio
CMD ["streamlit", "run", "Home.py", "--server.port=8501", "--server.address=0.0.0.0"]