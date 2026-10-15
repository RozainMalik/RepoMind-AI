import shutil
import traceback
from pathlib import Path
from urllib.parse import urlparse

from git import Repo
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.models.enums import RepositoryStatus
from app.models.repository import Repository
from app.schemas.repository import RepositoryCreate
from app.services.indexing_service import IndexingService
from app.services.qdrant_service import QdrantService


# Statuses that mean "a background job is working on this repository"
ACTIVE_STATUSES = {
    RepositoryStatus.PENDING.value,
    RepositoryStatus.INDEXING.value,
}


class RepositoryBusyError(Exception):
    """Raised when an action conflicts with an indexing job in progress."""


def remove_local_clone(local_path: str) -> None:
    path = Path(local_path)
    if path.exists():
        shutil.rmtree(path)


class RepositoryService:

    def __init__(self, db: Session):
        self.db = db

    # ---------- URL handling ----------

    def validate_github_url(self, github_url: str) -> tuple[str, str]:
        parsed = urlparse(github_url)

        if parsed.netloc not in {"github.com", "www.github.com"}:
            raise ValueError("Only GitHub repositories are supported.")

        parts = parsed.path.strip("/").split("/")

        if len(parts) != 2:
            raise ValueError(
                "GitHub URL must be in the format: https://github.com/<owner>/<repo>"
            )

        owner, repo = parts

        # Accept https://github.com/owner/repo.git
        if repo.endswith(".git"):
            repo = repo[:-4]

        if not owner or not repo:
            raise ValueError("Invalid GitHub repository URL.")

        return owner, repo

    def normalize_github_url(self, owner: str, repo: str) -> str:
        # One canonical form so ".../requests", ".../requests/" and
        # ".../requests.git" are all treated as the same repository
        return f"https://github.com/{owner}/{repo}"

    def generate_local_path(self, owner: str, repository_name: str) -> str:
        base_path = Path(__file__).resolve().parent.parent.parent
        repositories_path = base_path / "repositories"
        repositories_path.mkdir(exist_ok=True)

        # owner__repo avoids collisions like alice/api vs bob/api
        return str(repositories_path / f"{owner}__{repository_name}")

    def get_by_url(self, github_url: str) -> Repository | None:
        return (
            self.db.query(Repository)
            .filter(Repository.github_url == github_url)
            .first()
        )

    # ---------- Public API ----------

    def create_repository(
        self, repository_data: RepositoryCreate
    ) -> tuple[Repository, bool]:
        """Returns (repository, needs_indexing).

        Does NOT index. The endpoint schedules run_indexing() in the
        background when needs_indexing is True.
        """
        owner, repository_name = self.validate_github_url(
            str(repository_data.github_url)
        )
        github_url = self.normalize_github_url(owner, repository_name)

        existing = self.get_by_url(github_url)
        if existing:
            return self._handle_existing(existing)

        repository = Repository(
            github_url=github_url,
            name=repository_name,
            local_path=self.generate_local_path(owner, repository_name),
            status=RepositoryStatus.PENDING.value,
        )
        self.db.add(repository)

        try:
            self.db.commit()
        except IntegrityError:
            # Another request inserted the same URL a moment earlier.
            # The unique constraint caught it; use that row instead.
            self.db.rollback()
            return self._handle_existing(self.get_by_url(github_url))

        self.db.refresh(repository)
        return repository, True

    def _handle_existing(self, repository: Repository) -> tuple[Repository, bool]:
        # Already indexed, or a job is already running: don't start another
        if (
            repository.status == RepositoryStatus.READY.value
            or repository.status in ACTIVE_STATUSES
        ):
            return repository, False

        # FAILED: reset and index again on the same row
        repository.status = RepositoryStatus.PENDING.value
        self.db.commit()
        self.db.refresh(repository)
        return repository, True

    def list_repositories(self) -> list[Repository]:
        return (
            self.db.query(Repository)
            .order_by(Repository.created_at.desc())
            .all()
        )

    def delete_repository(self, repository_id: int) -> bool:
        repository = self.db.get(Repository, repository_id)

        if repository is None:
            return False

        # Deleting mid-index would race with the background job
        if repository.status in ACTIVE_STATUSES:
            raise RepositoryBusyError(
                "This repository is still being indexed. Try again when it finishes."
            )

        # Delete the row LAST: if vector or folder cleanup fails,
        # the row survives and the delete can simply be retried
        QdrantService().delete_repository_vectors(repository.id)
        remove_local_clone(repository.local_path)

        self.db.delete(repository)
        self.db.commit()

        return True


# ---------- Background job ----------

def run_indexing(repository_id: int) -> None:
    """Clone and index one repository. Runs after the HTTP response is sent.

    Opens its OWN database session: the request's session from get_db()
    is already closed by the time this runs.
    """
    db = SessionLocal()

    try:
        repository = db.get(Repository, repository_id)
        if repository is None:
            return

        repository.status = RepositoryStatus.INDEXING.value
        db.commit()

        try:
            # Clean up anything left behind by a previous failed attempt
            remove_local_clone(repository.local_path)
            QdrantService().delete_repository_vectors(repository.id)

            # depth=1: we only need the current files, not the full git history
            Repo.clone_from(repository.github_url, repository.local_path, depth=1)

            IndexingService().index_repository(
                repository.local_path,
                repository.id,
            )

            repository.status = RepositoryStatus.READY.value

        except Exception as e:
            traceback.print_exc()
            print(f"Indexing failed for repository {repository.id}: {e}")
            repository.status = RepositoryStatus.FAILED.value

        db.commit()

    finally:
        db.close()
