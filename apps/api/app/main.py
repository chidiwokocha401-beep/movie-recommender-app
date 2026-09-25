from fastapi import FastAPI

app = FastAPI(title="Movie Recommender API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
