# Gebruik Python 3.11 (stabiel en licht)
FROM python:3.11-slim

# Map in de container aanmaken
WORKDIR /app

# Systeemtools installeren (nodig voor cloudscraper en lxml)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Boodschappenlijstje kopiëren en installeren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Alle bestanden kopiëren (google_keys.json wordt uitgesloten via .dockerignore)
COPY . .

# Poort 8501 openzetten voor Streamlit
EXPOSE 8501

# De app starten
ENTRYPOINT ["streamlit", "run", "app_new.py", "--server.port=8501", "--server.address=0.0.0.0"]