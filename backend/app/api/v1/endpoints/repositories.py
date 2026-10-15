# from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
# from sqlalchemy.orm import Session

# from app.database.dependencies import get_db
# from app.schemas.repository import RepositoryCreate, RepositoryResponse
# from app.services.repository_service import (
#     RepositoryBusyError,
#     RepositoryService,
#     run_indexing,
# )

# router = APIRouter(prefix="/repositories", tags=["Repositories"])


# @router.get(
#     "",
#     response_model=list[RepositoryResponse],
# )

# @router.post(
#     "",
#     response_model=RepositoryResponse,
#     status_code=status.HTTP_202_ACCEPTED,
# )

# @router.delete(
#     "/{repository_id}",
#     status_code=status.HTTP_204_NO_CONTENT,
# )

# def delete_repository(
#     repository_id: int,
#     db: Session = Depends(get_db),
# ):
#     if not RepositoryService(db).delete_repository(repository_id):
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Repository not found.",
#         )
    
# def create_repository(
#     repository: RepositoryCreate,
#     background_tasks: BackgroundTasks,
#     db: Session = Depends(get_db),
# ):
#     try:
#         repo, needs_indexing = RepositoryService(db).create_repository(repository)

#     except ValueError as e:
#         # Invalid or non-GitHub URL
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(e),
#         )

#     # Respond immediately; cloning and indexing run after the response is sent.
#     # The client polls GET /repositories until the status is READY or FAILED.
#     if needs_indexing:
#         background_tasks.add_task(run_indexing, repo.id)

#     return repo


# @router.delete(
#     "/{repository_id}",
#     status_code=status.HTTP_204_NO_CONTENT,
# )
# def delete_repository(
#     repository_id: int,
#     db: Session = Depends(get_db),
# ):
#     try:
#         deleted = RepositoryService(db).delete_repository(repository_id)
#     except RepositoryBusyError as e:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail=str(e),
#         )

#     if not deleted:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Repository not found.",
#         )


from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.schemas.repository import RepositoryCreate, RepositoryResponse
from app.services.repository_service import (
    RepositoryBusyError,
    RepositoryService,
    run_indexing,
)

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
    status_code=status.HTTP_202_ACCEPTED,
)
def create_repository(
    repository: RepositoryCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    try:
        repo, needs_indexing = RepositoryService(db).create_repository(repository)

    except ValueError as e:
        # Invalid or non-GitHub URL
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Respond immediately; cloning and indexing run after the response is sent.
    # The client polls GET /repositories until the status is READY or FAILED.
    if needs_indexing:
        background_tasks.add_task(run_indexing, repo.id)

    return repo


@router.delete(
    "/{repository_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_repository(
    repository_id: int,
    db: Session = Depends(get_db),
):
    try:
        deleted = RepositoryService(db).delete_repository(repository_id)
    except RepositoryBusyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found.",
        )