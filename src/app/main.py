from fastapi import FastAPI

from src.app.routers import art

app = FastAPI()
app.include_router(art.router)


@app.get("/health", tags=["general"])
def health():
    return "ok"
