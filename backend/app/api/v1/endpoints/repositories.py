from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.schemas.repository import RepositoryCreate, RepositoryResponse
from app.services.repository_service import RepositoryService

router = APIRouter(prefix="/repositories", tags=["Repositories"])


@router.get(
    "",
    response_model=list[RepositoryResponse],
)
def list_repositories(db: Session = Depends(get_db)):
    return RepositoryService(db).list_repositories()


@router.post(
    "",
    response_model=RepositoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_repository(
    repository: RepositoryCreate,
    db: Session = Depends(get_db),
):
    try:
        # Returns the existing record if the repository is already indexed
        return RepositoryService(db).create_repository(repository)

    except ValueError as e:
        # Invalid or non-GitHub URL
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/{repository_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_repository(
    repository_id: int,
    db: Session = Depends(get_db),
):
    if not RepositoryService(db).delete_repository(repository_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found.",
        )