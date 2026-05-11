ARG PYTHON_IMAGE=python:3.13-slim
FROM ${PYTHON_IMAGE}

ARG FREQTRADE_VERSION=2026.4
ARG FT_UID=1000
ARG FT_GID=1000

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    git \
    libgomp1 \
  && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip setuptools wheel \
  && python -m pip install "freqtrade==${FREQTRADE_VERSION}"

RUN groupadd --gid "${FT_GID}" ftuser \
  && useradd --uid "${FT_UID}" --gid "${FT_GID}" --create-home --shell /bin/bash ftuser \
  && mkdir -p /freqtrade \
  && chown -R ftuser:ftuser /freqtrade /home/ftuser

USER ftuser
WORKDIR /freqtrade

ENTRYPOINT ["freqtrade"]
CMD ["trade"]
