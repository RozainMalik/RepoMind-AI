from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints.repositories import router as repository_router
from app.database.session import SessionLocal
from app.models.enums import RepositoryStatus
from app.models.repository import Repository
from app.routes.chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Background jobs live inside this process, so they die on restart.
    # Anything still PENDING/INDEXING at startup was interrupted:
    # mark it FAILED so the user can retry instead of waiting forever.
    db = SessionLocal()
    try:
        db.query(Repository).filter(
            Repository.status.in_(
                [RepositoryStatus.PENDING.value, RepositoryStatus.INDEXING.value]
            )
        ).update(
            {Repository.status: RepositoryStatus.FAILED.value},
            synchronize_session=False,
        )
        db.commit()
    finally:
        db.close()

    yield


app = FastAPI(title="RepoMind AI", lifespan=lifespan)

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
