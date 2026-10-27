from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.internal.command_services.default_learning_path_command_service import DefaultLearningPathCommandService
from app.application.internal.query_service.default_learning_path_query_service import DefaultLearningPathQueryService
from app.dependencies import get_current_user_id, get_db_session, get_learning_path_command_service, get_learning_path_query_service
from app.domain.model.commands.mark_learning_path_item_watched_command import MarkLearningPathItemWatchedCommand
from app.domain.model.queries.get_learning_path_by_job_query import GetLearningPathByJobQuery
from app.domain.model.queries.get_learning_path_progress_query import GetLearningPathProgressQuery
from app.interfaces.rest.resources.generate_learning_path_resource import GenerateLearningPathResource
from app.interfaces.rest.resources.learning_path_resource import LearningPathProgressResource, LearningPathResource
from app.interfaces.rest.transform.generate_learning_path_command_from_resource_assembler import GenerateLearningPathCommandFromResourceAssembler
from app.interfaces.rest.transform.learning_path_resource_from_entity_assembler import LearningPathResourceFromEntityAssembler


router = APIRouter(prefix="/api/v1/learning-paths", tags=["Learning Pathway"])


@router.post("", response_model=LearningPathResource, status_code=status.HTTP_201_CREATED)
async def generate_learning_path(
    resource: GenerateLearningPathResource,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> LearningPathResource:
    service: DefaultLearningPathCommandService = get_learning_path_command_service(session)
    try:
        learning_path = await service.handle_generate(
            GenerateLearningPathCommandFromResourceAssembler.to_command(user_id, resource)
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return LearningPathResourceFromEntityAssembler.to_resource(learning_path)


@router.get("/{job_id}", response_model=LearningPathResource)
async def get_learning_path(
    job_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> LearningPathResource:
    service: DefaultLearningPathQueryService = get_learning_path_query_service(session)
    learning_path = await service.handle_get_by_job(GetLearningPathByJobQuery(user_id=user_id, job_id=job_id))
    if learning_path is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning path not found.")
    return LearningPathResourceFromEntityAssembler.to_resource(learning_path)


@router.patch("/{learning_path_id}/items/{item_id}", response_model=LearningPathResource)
async def mark_learning_path_item_watched(
    learning_path_id: int,
    item_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> LearningPathResource:
    service: DefaultLearningPathCommandService = get_learning_path_command_service(session)
    try:
        learning_path = await service.handle_mark_item_watched(
            MarkLearningPathItemWatchedCommand(
                user_id=user_id,
                learning_path_id=learning_path_id,
                item_id=item_id,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return LearningPathResourceFromEntityAssembler.to_resource(learning_path)


@router.get("/{learning_path_id}/progress", response_model=LearningPathProgressResource)
async def get_learning_path_progress(
    learning_path_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> LearningPathProgressResource:
    service: DefaultLearningPathQueryService = get_learning_path_query_service(session)
    learning_path = await service.handle_get_progress(
        GetLearningPathProgressQuery(user_id=user_id, learning_path_id=learning_path_id)
    )
    if learning_path is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning path not found.")
    return LearningPathResourceFromEntityAssembler.to_progress_resource(learning_path)
