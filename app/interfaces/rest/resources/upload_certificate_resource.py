from pydantic import BaseModel, Field


class UploadCertificateResource(BaseModel):
    learning_path_id: int = Field(gt=0)
    skill_name: str = Field(min_length=1, max_length=100)
    provider: str | None = Field(default=None, max_length=150)
