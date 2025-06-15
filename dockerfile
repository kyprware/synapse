FROM python:3.11-slim

WORKDIR /app

COPY packages.apt .
RUN apt-get update && \
    xargs -a packages.apt apt-get install -y --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

COPY cert-gen.sh entrypoint.sh ./
RUN chmod +x entrypoint.sh cert-gen.sh

RUN python -m pip install --upgrade pip

COPY requirements.txt requirements.dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements.dev.txt

COPY synapse/ synapse/
COPY tests/ tests/

RUN mkdir -p certs && chmod 755 certs

ENTRYPOINT ["./entrypoint.sh"]

CMD ["python", "-m", "synapse"]
