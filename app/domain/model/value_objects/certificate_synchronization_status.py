from enum import Enum


class CertificateSynchronizationStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    SYNCHRONIZED = "synchronized"
    FAILED = "failed"
