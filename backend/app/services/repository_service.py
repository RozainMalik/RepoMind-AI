from pathlib import Path
from urllib.parse import urlparse
from sqlalchemy.orm import Session
from app.models.repository import Repository
from app.models.enums import RepositoryStatus
from app.schemas.repository import RepositoryCreate
from git import Repo
from app.services.chunking_service import ChunkingService
from app.services.parser_service import ParserService
from app.services.indexing_service import IndexingService
import traceback
class RepositoryService:

    def __init__(self, db: Session):
        self.db = db


    # def extract_repository_name(self, github_url: str) -> str: # extract the name to store locally
    #     path = urlparse(github_url).path.strip("/")
    #     return path.split("/")[-1]

    def generate_local_path(self, repository_name: str) -> str:
        base_path = Path(__file__).resolve().parent.parent.parent
        repositories_path = base_path / "repositories"
        repositories_path.mkdir(exist_ok=True)

        return str(repositories_path / repository_name)

    def repository_exists(self, github_url: str) -> bool: # check if the repo already exists if yes show repo already exists
        return (
            self.db.query(Repository)
            .filter(Repository.github_url == github_url)
            .first()
            is not None
        )
    
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

        if not owner or not repo:
            raise ValueError("Invalid GitHub repository URL.")

        return owner, repo

    def create_repository(
        self,
        repository_data: RepositoryCreate,
    ) -> Repository:

        github_url = str(repository_data.github_url)

        owner, repository_name = self.validate_github_url(github_url)

        if self.repository_exists(github_url):
            raise ValueError("Repository already exists.")

        repository = Repository(
            github_url=github_url,
            name=repository_name,
            local_path=self.generate_local_path(repository_name),
            status=RepositoryStatus.PENDING.value,
        )

        self.db.add(repository)
        self.db.commit()
        self.db.refresh(repository)

        try:
            self.clone_repository(repository.github_url, repository.local_path, )

            indexer = IndexingService()

            indexer.index_repository(
                repository.local_path,
                repository.id,
            )

            repository.status = RepositoryStatus.READY.value

        except Exception as e:
            traceback.print_exc()
            print(f"Error: {e}")
            repository.status = RepositoryStatus.FAILED.value

        self.db.commit()
        self.db.refresh(repository)

        return repository
    
    #cloning using gitpython
    def clone_repository(
        self,
            github_url: str,
            local_path: str,
        ):
            Repo.clone_from(github_url, local_path)

    # def process_repository(self, repository_path: str):
    #     parser = ParserService()
    #     chunker = ChunkingService()

    #     files = parser.get_source_files(repository_path)

    #     all_chunks = []

    #     for file in files:
    #         all_chunks.extend(chunker.chunk_file(file))

    #     return all_chunks