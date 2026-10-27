from dataclasses import dataclass


@dataclass(frozen=True)
class UploadCertificateCommand:
    user_id: int
    learning_path_id: int
    skill_name: str
    provider: str | None
    original_filename: str
    content_type: str
    content: bytes
