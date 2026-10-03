from fastapi import FastAPI

from app.api.v1.endpoints.repositories import router as repository_router
from app.routes.chat import router as chat_router

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="RepoMind AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    repository_router,
    prefix="/api/v1"
)

app.include_router(
    chat_router,
    prefix="/api/v1"
)
