from collections.abc import AsyncGenerator

from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.internal.command_services.default_learning_path_command_service import DefaultLearningPathCommandService
from app.application.internal.command_services.default_learning_path_recommendation_service import DefaultLearningPathRecommendationService
from app.application.internal.query_service.default_learning_path_query_service import DefaultLearningPathQueryService
from app.infrastructure.clients.gap_analysis_service_client import GapAnalysisServiceClient
from app.infrastructure.clients.youtube_data_api_client import YouTubeDataApiClient
from app.infrastructure.configuration.settings import get_settings
from app.infrastructure.persistence.sqlalchemy.database import get_session
from app.infrastructure.persistence.sqlalchemy.repositories.sqlalchemy_learning_path_repository import SQLAlchemyLearningPathRepository


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


def get_current_user_id(request: Request) -> int:
    header = get_settings().gateway_user_id_header
    raw_user_id = request.headers.get(header)
    if raw_user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Missing gateway identity header: {header}")
    try:
        user_id = int(raw_user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid gateway user identifier.") from exc
    if user_id <= 0:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid gateway user identifier.")
    return user_id


def get_learning_path_recommendation_service() -> DefaultLearningPathRecommendationService:
    settings = get_settings()
    return DefaultLearningPathRecommendationService(
        gap_analysis_client=GapAnalysisServiceClient(settings.gap_analysis_service_url, settings.gateway_user_id_header),
        youtube_video_search_client=YouTubeDataApiClient(settings.youtube_data_api_key),
    )


def get_learning_path_command_service(session: AsyncSession) -> DefaultLearningPathCommandService:
    return DefaultLearningPathCommandService(
        recommendation_service=get_learning_path_recommendation_service(),
        repository=SQLAlchemyLearningPathRepository(session),
        commit=session.commit,
    )


def get_learning_path_query_service(session: AsyncSession) -> DefaultLearningPathQueryService:
    return DefaultLearningPathQueryService(SQLAlchemyLearningPathRepository(session))
