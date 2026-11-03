from pydantic import BaseModel, Field


class GenerateLearningPathResource(BaseModel):
    job_id: int = Field(
        gt=0,
        examples=[1],
        description="ID de un empleo con un reporte de brechas ya generado.",
    )
