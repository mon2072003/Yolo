FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx libglib2.0-0 gcc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir torch==2.7.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

COPY . .

CMD ["sh", "-c", "gunicorn main:app --bind 0.0.0.0:$PORT"]
