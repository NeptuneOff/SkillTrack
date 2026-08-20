FROM python:3.12-slim AS common

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 skilltrack \
    && useradd --uid 10001 --gid skilltrack --create-home skilltrack

COPY pyproject.toml requirements.lock ./
COPY app ./app
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.lock \
    && pip install --no-cache-dir --no-deps . \
    && pip check

RUN chown -R skilltrack:skilltrack /app

EXPOSE 8000

FROM common AS production
USER skilltrack
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--proxy-headers"]

FROM common AS development
USER root
COPY requirements-dev.lock ./
COPY tests ./tests
RUN pip install --no-cache-dir -r requirements-dev.lock \
    && pip check \
    && chown -R skilltrack:skilltrack /app
USER skilltrack
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
