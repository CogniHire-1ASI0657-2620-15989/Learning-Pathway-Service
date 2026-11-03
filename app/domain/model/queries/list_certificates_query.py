from dataclasses import dataclass


@dataclass(frozen=True)
class ListCertificatesQuery:
    user_id: int
    learning_path_id: int | None = None
