from io import BytesIO

import pytest
from PIL import Image

from app.application.internal.command_services.default_certificate_validation_service import (
    DefaultCertificateValidationService,
)
from app.application.ports.identity_profile_client import UserProfile
from app.domain.model.value_objects.certificate_status import CertificateStatus
from app.infrastructure.ocr.certificate_content_validator import CertificateContentValidator


class FakeTextExtractor:
    def __init__(self, text: str):
        self._text = text

    async def extract_text(self, content: bytes, content_type: str) -> str:
        return self._text


class FakeIdentityProfileClient:
    async def get_user_profile(self, user_id: int) -> UserProfile:
        assert user_id == 7
        return UserProfile(user_id=7, name="Ana Pérez")


@pytest.mark.asyncio
async def test_approves_certificate_when_name_skill_and_provider_match() -> None:
    service = DefaultCertificateValidationService(
        FakeTextExtractor("Certificado para ANA PEREZ por completar el curso de SQL en Udemy."),
        FakeIdentityProfileClient(),
    )

    result = await service.validate(7, "SQL", "Udemy", b"content", "application/pdf")

    assert result.status == CertificateStatus.APPROVED
    assert result.detected_name == "Ana Pérez"
    assert result.detected_course_title == "SQL"
    assert result.detected_provider == "Udemy"


@pytest.mark.asyncio
async def test_marks_name_mismatch_when_certificate_holder_is_different() -> None:
    service = DefaultCertificateValidationService(
        FakeTextExtractor("Certificado para Carlos Gómez por completar el curso de SQL."),
        FakeIdentityProfileClient(),
    )

    result = await service.validate(7, "SQL", None, b"content", "application/pdf")

    assert result.status == CertificateStatus.NAME_MISMATCH


@pytest.mark.asyncio
async def test_marks_course_mismatch_when_target_skill_is_not_found() -> None:
    service = DefaultCertificateValidationService(
        FakeTextExtractor("Certificado para Ana Pérez por completar el curso de Docker."),
        FakeIdentityProfileClient(),
    )

    result = await service.validate(7, "SQL", None, b"content", "application/pdf")

    assert result.status == CertificateStatus.COURSE_MISMATCH


def test_accepts_a_valid_png_certificate_upload() -> None:
    image = Image.new("RGB", (16, 16), color="white")
    content = BytesIO()
    image.save(content, format="PNG")

    CertificateContentValidator.validate(content.getvalue(), "image/png")


def test_rejects_a_file_that_does_not_match_its_claimed_content_type() -> None:
    with pytest.raises(ValueError, match="PDF válido"):
        CertificateContentValidator.validate(b"not a PDF", "application/pdf")
