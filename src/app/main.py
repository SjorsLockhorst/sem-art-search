from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.routers import art

app = FastAPI()
app.include_router(art.router)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["general"])
def health():
    return "ok"
