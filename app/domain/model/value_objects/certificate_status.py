from enum import Enum


class CertificateStatus(str, Enum):
    PROCESSING = "processing"
    APPROVED = "approved"
    NAME_MISMATCH = "name_mismatch"
    COURSE_MISMATCH = "course_mismatch"
    UNREADABLE = "unreadable"
    NEEDS_REVIEW = "needs_review"
