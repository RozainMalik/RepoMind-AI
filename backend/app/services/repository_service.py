import shutil
import traceback
from pathlib import Path
from urllib.parse import urlparse

from git import Repo
from sqlalchemy.orm import Session

from app.models.enums import RepositoryStatus
from app.models.repository import Repository
from app.schemas.repository import RepositoryCreate
from app.services.indexing_service import IndexingService
from app.services.qdrant_service import QdrantService


class RepositoryService:

    def __init__(self, db: Session):
        self.db = db

    # ---------- URL handling ----------

    def validate_github_url(self, github_url: str) -> tuple[str, str]:
        parsed = urlparse(github_url)

        if parsed.netloc != "github.com":
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

    def create_repository(self, repository_data: RepositoryCreate) -> Repository:
        owner, repository_name = self.validate_github_url(
            str(repository_data.github_url)
        )
        github_url = self.normalize_github_url(owner, repository_name)

        existing = self.get_by_url(github_url)

        if existing:
            if existing.status == RepositoryStatus.READY.value:
                # Already indexed: hand it back so the frontend can use its ID
                return existing

            # FAILED, or PENDING left over from a crashed run: retry on the same record
            return self._clone_and_index(existing)

        repository = Repository(
            github_url=github_url,
            name=repository_name,
            local_path=self.generate_local_path(owner, repository_name),
            status=RepositoryStatus.PENDING.value,
        )

        self.db.add(repository)
        self.db.commit()
        self.db.refresh(repository)

        return self._clone_and_index(repository)

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

        # Delete the row LAST: if vector or folder cleanup fails,
        # the row survives and the delete can simply be retried
        QdrantService().delete_repository_vectors(repository.id)
        self._remove_local_clone(repository.local_path)

        self.db.delete(repository)
        self.db.commit()

        return True

    # ---------- Pipeline ----------

    def _clone_and_index(self, repository: Repository) -> Repository:
        repository.status = RepositoryStatus.PENDING.value
        self.db.commit()

        try:
            # Clean up anything left behind by a previous failed attempt
            self._remove_local_clone(repository.local_path)
            QdrantService().delete_repository_vectors(repository.id)

            self.clone_repository(repository.github_url, repository.local_path)

            IndexingService().index_repository(
                repository.local_path,
                repository.id,
            )

            repository.status = RepositoryStatus.READY.value

        except Exception as e:
            traceback.print_exc()
            print(f"Indexing failed for repository {repository.id}: {e}")
            repository.status = RepositoryStatus.FAILED.value

        self.db.commit()
        self.db.refresh(repository)

        return repository

    def clone_repository(self, github_url: str, local_path: str):
        # depth=1: we only need the current files, not the full git history
        Repo.clone_from(github_url, local_path, depth=1)

    def _remove_local_clone(self, local_path: str):
        path = Path(local_path)
        if path.exists():
            shutil.rmtree(path)