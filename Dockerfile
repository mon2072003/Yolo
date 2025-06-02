FROM python:3.12-slim

# تثبيت الحزم النظامية (اختياري)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libgl1-mesa-glx libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# استخدم صيغة شل لتوسيع $PORT
CMD ["sh", "-c", "gunicorn main:app --bind 0.0.0.0:$PORT"]
