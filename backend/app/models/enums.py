from enum import Enum


class RepositoryStatus(str, Enum):
    PENDING = "PENDING"
    INDEXING = "INDEXING"
    READY = "READY"
    FAILED = "FAILED"