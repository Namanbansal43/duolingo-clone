# The FastAPI backend. On start it brings the SQLite schema up to date and seeds anything missing,
# so a new, empty volume becomes a working demo on the first boot.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY alembic.ini .
COPY alembic ./alembic
COPY app ./app

# The database lives on a volume mounted at /data, so progress survives restarts and redeploys.
# The process runs as root because hosting platforms mount volumes owned by root.
ENV DATABASE_URL=sqlite:////data/app.db
RUN mkdir -p /data

EXPOSE 8000

# One worker: SQLite allows a single writer, and the app's lazy updates (rival XP, league weeks) write on
# read. The platform sets PORT; 8000 is the fallback for running the image locally.
CMD ["sh", "-c", "exec uvicorn app.main:create_app --factory --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]
