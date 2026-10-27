from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.internal.command_services.default_certificate_command_service import DefaultCertificateCommandService
from app.application.internal.query_service.default_certificate_query_service import DefaultCertificateQueryService
from app.dependencies import get_certificate_command_service, get_certificate_query_service, get_current_user_id, get_db_session
from app.domain.model.queries.get_certificate_by_id_query import GetCertificateByIdQuery
from app.infrastructure.ocr.certificate_content_validator import CertificateContentValidator
from app.interfaces.rest.resources.certificate_resource import CertificateResource
from app.interfaces.rest.resources.upload_certificate_resource import UploadCertificateResource
from app.interfaces.rest.transform.certificate_resource_from_entity_assembler import CertificateResourceFromEntityAssembler
from app.interfaces.rest.transform.upload_certificate_command_from_resource_assembler import UploadCertificateCommandFromResourceAssembler


router = APIRouter(prefix="/api/v1/certificates", tags=["Certificates"])


@router.post("", response_model=CertificateResource, status_code=status.HTTP_201_CREATED)
async def upload_certificate(
    learning_path_id: Annotated[int, Form(gt=0)],
    skill_name: Annotated[str, Form(min_length=1, max_length=100)],
    file: Annotated[UploadFile, File()],
    provider: Annotated[str | None, Form(max_length=150)] = None,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> CertificateResource:
    content = await file.read()
    content_type = file.content_type or ""
    try:
        CertificateContentValidator.validate(content, content_type)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    resource = UploadCertificateResource(
        learning_path_id=learning_path_id,
        skill_name=skill_name,
        provider=provider.strip() if provider and provider.strip() else None,
    )
    service: DefaultCertificateCommandService = get_certificate_command_service(session)
    try:
        certificate = await service.handle_upload(
            UploadCertificateCommandFromResourceAssembler.to_command(
                user_id=user_id,
                resource=resource,
                original_filename=file.filename or "certificate",
                content_type=content_type,
                content=content,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return CertificateResourceFromEntityAssembler.to_resource(certificate)


@router.get("/{certificate_id}", response_model=CertificateResource)
async def get_certificate(
    certificate_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> CertificateResource:
    service: DefaultCertificateQueryService = get_certificate_query_service(session)
    certificate = await service.handle_get_by_id(GetCertificateByIdQuery(user_id=user_id, certificate_id=certificate_id))
    if certificate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found.")
    return CertificateResourceFromEntityAssembler.to_resource(certificate)
