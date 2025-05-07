FROM python:3.12-slim

WORKDIR /usr/src/app

RUN apt-get update && \
    apt-get install -y --no-install-recommends npm && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY package*.json ./
RUN npm install --no-audit --no-fund

COPY . .

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8000", "main:app"]