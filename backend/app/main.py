from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import art

app = FastAPI()
app.include_router(art.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["general"])
def health():
    return "ok"
