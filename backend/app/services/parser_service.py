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
        ".idea",
        ".vscode",
        ".pytest_cache",
        ".mypy_cache",
        ".pre-commit-config.yaml",
        "LICENSE.txt",
        ".readthedocs.yaml"
    }

    SUPPORTED_EXTENSIONS = {
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".java",
        ".cpp",
        ".c",
        ".h",
        ".hpp",
        ".go",
        ".rs",
        ".md",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".txt",
        ".sql",
        ".sh",
    }

    def get_source_files(self, repository_path: str) -> list[Path]:
        repository = Path(repository_path)

        source_files = []

        for file in repository.rglob("*"):

            if not file.is_file():
                continue

            # Skip ignored directories
            if any(part in self.IGNORE_DIRECTORIES for part in file.parts):
                continue

            # Skip unsupported file types
            if file.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                continue

            source_files.append(file)

        return source_files