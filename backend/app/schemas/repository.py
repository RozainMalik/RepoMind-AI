from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl


class RepositoryCreate(BaseModel):
    github_url: HttpUrl


class RepositoryResponse(BaseModel):
    id: int
    github_url: HttpUrl
    name: str
    local_path: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)