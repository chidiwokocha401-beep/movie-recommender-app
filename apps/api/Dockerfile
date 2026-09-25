FROM python:3.12-slim

WORKDIR /srv

COPY packages/recommender ./packages/recommender
COPY apps/api ./apps/api
COPY db ./db
COPY movie-recommender-main/u.data ./movie-recommender-main/u.data
COPY movie-recommender-main/u.item ./movie-recommender-main/u.item

RUN pip install --no-cache-dir -e ./apps/api -e "./packages/recommender[postgres,redis]"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "/srv/apps/api"]
