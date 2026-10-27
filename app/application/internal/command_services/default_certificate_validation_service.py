import re
import unicodedata
from dataclasses import dataclass

from app.application.ports.certificate_text_extractor import CertificateTextExtractor
from app.application.ports.identity_profile_client import IdentityProfileClient
from app.domain.model.value_objects.certificate_status import CertificateStatus


@dataclass(frozen=True)
class CertificateValidationResult:
    status: CertificateStatus
    extracted_text: str | None
    detected_name: str | None
    detected_course_title: str | None
    detected_provider: str | None
    validation_detail: str


class DefaultCertificateValidationService:
    MINIMUM_TEXT_LENGTH = 10

    def __init__(self, text_extractor: CertificateTextExtractor, identity_profile_client: IdentityProfileClient):
        self._text_extractor = text_extractor
        self._identity_profile_client = identity_profile_client

    async def validate(
        self,
        user_id: int,
        skill_name: str,
        provider: str | None,
        content: bytes,
        content_type: str,
    ) -> CertificateValidationResult:
        extracted_text = (await self._text_extractor.extract_text(content, content_type)).strip()
        normalized_text = self._normalize(extracted_text)
        if len(normalized_text) < self.MINIMUM_TEXT_LENGTH:
            return CertificateValidationResult(
                status=CertificateStatus.UNREADABLE,
                extracted_text=extracted_text or None,
                detected_name=None,
                detected_course_title=None,
                detected_provider=None,
                validation_detail="No se pudo extraer texto suficiente del certificado.",
            )

        profile = await self._identity_profile_client.get_user_profile(user_id)
        expected_name = self._normalize(profile.name)
        if expected_name not in normalized_text:
            return CertificateValidationResult(
                status=CertificateStatus.NAME_MISMATCH,
                extracted_text=extracted_text,
                detected_name=None,
                detected_course_title=None,
                detected_provider=None,
                validation_detail="El nombre del certificado no coincide con el perfil del usuario.",
            )

        normalized_skill = self._normalize(skill_name)
        if normalized_skill not in normalized_text:
            return CertificateValidationResult(
                status=CertificateStatus.COURSE_MISMATCH,
                extracted_text=extracted_text,
                detected_name=profile.name,
                detected_course_title=None,
                detected_provider=None,
                validation_detail="El certificado no menciona la habilidad objetivo de la ruta.",
            )

        detected_provider = None
        if provider:
            if self._normalize(provider) not in normalized_text:
                return CertificateValidationResult(
                    status=CertificateStatus.NEEDS_REVIEW,
                    extracted_text=extracted_text,
                    detected_name=profile.name,
                    detected_course_title=skill_name,
                    detected_provider=None,
                    validation_detail="No se pudo confirmar el proveedor declarado del certificado.",
                )
            detected_provider = provider

        return CertificateValidationResult(
            status=CertificateStatus.APPROVED,
            extracted_text=extracted_text,
            detected_name=profile.name,
            detected_course_title=skill_name,
            detected_provider=detected_provider,
            validation_detail="El certificado coincide con el usuario y la habilidad objetivo.",
        )

    @staticmethod
    def _normalize(value: str) -> str:
        decomposed = unicodedata.normalize("NFKD", value)
        without_accents = "".join(character for character in decomposed if not unicodedata.combining(character))
        return re.sub(r"\s+", " ", without_accents).strip().casefold()
