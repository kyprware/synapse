FROM python:3.11-slim

WORKDIR /app

RUN python -m pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY requirements.dev.txt .
RUN pip install --no-cache-dir -r requirements.dev.txt

COPY synapse/ synapse/
COPY tests/ tests/
