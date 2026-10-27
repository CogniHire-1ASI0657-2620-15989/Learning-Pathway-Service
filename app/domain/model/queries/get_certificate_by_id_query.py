from dataclasses import dataclass


@dataclass(frozen=True)
class GetCertificateByIdQuery:
    user_id: int
    certificate_id: int
