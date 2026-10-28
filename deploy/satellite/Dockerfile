# syntax=docker/dockerfile:1
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN --mount=type=secret,id=proxy_ca \
    satellite_ca=/etc/ssl/certs/ca-certificates.crt; \
    if [ -f /run/secrets/proxy_ca ]; then satellite_ca=/run/secrets/proxy_ca; fi; \
    apt-get -o Acquire::https::CaInfo="$satellite_ca" update && \
    apt-get -o Acquire::https::CaInfo="$satellite_ca" install -y --no-install-recommends libexpat1 && \
    rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./requirements.txt
RUN --mount=type=secret,id=proxy_ca \
    if [ -f /run/secrets/proxy_ca ]; then export PIP_CERT=/run/secrets/proxy_ca; fi; \
    pip install --no-cache-dir -r requirements.txt
COPY satellite ./satellite
CMD ["python", "-m", "satellite.run"]
