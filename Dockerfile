# استخدم صورة بايثون خفيفة
FROM python:3.12-slim

# 1. ثبّت مكتبات النظام المطلوبة لـ OpenCV (libGL و libglib)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libgl1-mesa-glx \
      libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/* \
    # مصادر تثبيت libGL و libglib :contentReference[oaicite:0]{index=0}

# 2. حدّد مجلد العمل ونسخ ملف المتطلبات
WORKDIR /app
COPY requirements.txt .

# 3. ثبّت بايثون باكجات
RUN pip install --no-cache-dir -r requirements.txt

# 4. نسخ باقي ملفات المشروع
COPY . .

# 5. أمر التشغيل، يقرأ PORT من البيئة ويستمع على 0.0.0.0
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:$PORT"]
