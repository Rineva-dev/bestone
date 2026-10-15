# Base image Python
FROM python:3.11-slim

# Folder kerja di dalam container
WORKDIR /app

# Instal dependensi sistem
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Salin & pasang paket Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua kode aplikasi
COPY . .

# Port yang dibuka
EXPOSE 5000

# Perintah jalankan aplikasi
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "60", "app:app"]