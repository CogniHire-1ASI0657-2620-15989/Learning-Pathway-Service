from pydantic import BaseModel, Field


class GenerateLearningPathResource(BaseModel):
    job_id: int = Field(gt=0)
