from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json

from app.database.connection import init_db
from app.routes import logs, stats, productivity, categories

app = FastAPI(
    title="Analisador de Hábitos Digitais",
    description="API para coleta e análise de comportamento digital",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(logs.router)
app.include_router(stats.router)
app.include_router(productivity.router)
app.include_router(categories.router)


@app.middleware("http")
async def utf8_charset(request: Request, call_next):
    response = await call_next(request)
    if response.headers.get("content-type", "").startswith("application/json"):
        response.headers["content-type"] = "application/json; charset=utf-8"
    return response


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/", tags=["health"])
def root():
    return {
        "status": "ok",
        "docs": "/docs",
        "endpoints": ["/logs", "/stats", "/productivity", "/categories"],
    }


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
