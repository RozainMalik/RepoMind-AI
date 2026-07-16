from fastapi import FastAPI

from app.api.v1.endpoints.repositories import router as repository_router

app = FastAPI(title="RepoMind AI")

app.include_router(
    repository_router,
    prefix="/api/v1",
)