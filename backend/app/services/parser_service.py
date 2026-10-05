from pathlib import Path


class ParserService:

    IGNORE_DIRECTORIES = {
        ".git",
        "__pycache__",
        "node_modules",
        "venv",
        ".venv",
        "env",
        "dist",
        "build",
        "bin",
        "obj",
        "target",
        "coverage",
        ".next",
        ".idea",
        ".vscode",
        ".pytest_cache",
        ".mypy_cache",
    }

    # Exact file names that add noise but no understanding
    IGNORE_FILES = {
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "poetry.lock",
        "Pipfile.lock",
        "composer.lock",
        "LICENSE",
        "LICENSE.txt",
        ".pre-commit-config.yaml",
        ".readthedocs.yaml",
    }

    SUPPORTED_EXTENSIONS = {
        # Backend languages
        ".py", ".java", ".cs", ".go", ".rs", ".rb", ".php", ".kt", ".swift",
        ".c", ".cpp", ".h", ".hpp",
        # Frontend
        ".js", ".jsx", ".ts", ".tsx", ".vue", ".html", ".css", ".scss",
        # Docs, config, data definitions
        ".md", ".json", ".yaml", ".yml", ".toml", ".xml", ".txt",
        ".sql", ".sh",
    }

    # Files without a useful extension
    SUPPORTED_FILENAMES = {"Dockerfile", "Makefile"}

    # Skip generated/minified/data files bigger than this
    MAX_FILE_BYTES = 300_000

    def get_source_files(self, repository_path: str) -> list[Path]:
        repository = Path(repository_path)

        source_files = []

        for file in repository.rglob("*"):

            if not file.is_file():
                continue

            # Check only the part of the path INSIDE the repository, so a
            # parent folder called "build" or "env" can't hide everything
            relative_parts = file.relative_to(repository).parts

            if any(part in self.IGNORE_DIRECTORIES for part in relative_parts[:-1]):
                continue

            if file.name in self.IGNORE_FILES:
                continue

            if file.name.endswith((".min.js", ".min.css")):
                continue

            supported = (
                file.suffix.lower() in self.SUPPORTED_EXTENSIONS
                or file.name in self.SUPPORTED_FILENAMES
            )
            if not supported:
                continue

            try:
                if file.stat().st_size > self.MAX_FILE_BYTES:
                    continue
            except OSError:
                continue

            source_files.append(file)

        return source_files