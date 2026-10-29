from datetime import UTC, datetime

import pytest
import respx
from httpx import Response

from app.application.ports.gap_analysis_client import GapAnalysisReport, MissingSkill
from app.application.ports.youtube_video_search_client import YouTubeVideo
from app.application.internal.command_services.default_learning_path_recommendation_service import (
    DefaultLearningPathRecommendationService,
)
from app.infrastructure.clients.gap_analysis_service_client import GapAnalysisServiceClient
from app.infrastructure.clients.youtube_data_api_client import YouTubeDataApiClient


@respx.mock
@pytest.mark.asyncio
async def test_gets_missing_hard_skills_from_gap_analysis() -> None:
    route = respx.get("http://gap-analysis:8000/api/v1/gap-reports/44").mock(
        return_value=Response(
            200,
            json={
                "id": 9,
                "job_id": 44,
                "updated_at": "2026-10-27T12:00:00Z",
                "missing_hard_skills": [
                    {"name": "SQL", "skill_type": "hard"},
                    {"name": "Docker", "skill_type": "hard"},
                ],
            },
        )
    )

    report = await GapAnalysisServiceClient("http://gap-analysis:8000", "X-User-Id").get_report(7, 44)

    assert route.called
    assert route.calls.last.request.headers["X-User-Id"] == "7"
    assert report.id == 9
    assert report.missing_hard_skills == [MissingSkill("SQL", "hard"), MissingSkill("Docker", "hard")]


@respx.mock
@pytest.mark.asyncio
async def test_regenerates_gap_report_after_a_verified_skill_is_promoted() -> None:
    route = respx.post("http://gap-analysis:8000/api/v1/gap-reports").mock(
        return_value=Response(
            201,
            json={
                "id": 9,
                "job_id": 44,
                "updated_at": "2026-10-27T12:00:00Z",
                "missing_hard_skills": [],
            },
        )
    )

    report = await GapAnalysisServiceClient("http://gap-analysis:8000", "X-User-Id").regenerate_report(7, 44)

    assert route.called
    assert route.calls.last.request.headers["X-User-Id"] == "7"
    assert route.calls.last.request.content == b'{"job_id":44}'
    assert report.missing_hard_skills == []


@respx.mock
@pytest.mark.asyncio
async def test_searches_youtube_videos_by_skill() -> None:
    route = respx.get("https://www.googleapis.com/youtube/v3/search").mock(
        return_value=Response(
            200,
            json={
                "items": [
                    {
                        "id": {"videoId": "sql-video"},
                        "snippet": {
                            "title": "SQL desde cero",
                            "channelTitle": "Canal SQL",
                            "description": "Aprende SQL.",
                            "thumbnails": {"high": {"url": "https://img.example/sql.jpg"}},
                        },
                    }
                ]
            },
        )
    )

    videos = await YouTubeDataApiClient("test-key").search_videos("SQL", 3)

    assert route.called
    assert route.calls.last.request.url.params["q"] == "SQL"
    assert route.calls.last.request.url.params["maxResults"] == "3"
    assert route.calls.last.request.url.params["videoDuration"] == "long"
    assert route.calls.last.request.url.params["relevanceLanguage"] == "es"
    assert videos == [
        YouTubeVideo(
            video_id="sql-video",
            title="SQL desde cero",
            channel_title="Canal SQL",
            description="Aprende SQL.",
            url="https://www.youtube.com/watch?v=sql-video",
            thumbnail_url="https://img.example/sql.jpg",
        )
    ]


class FakeGapAnalysisClient:
    async def get_report(self, user_id: int, job_id: int) -> GapAnalysisReport:
        assert (user_id, job_id) == (7, 44)
        return GapAnalysisReport(
            id=9,
            job_id=44,
            updated_at=datetime(2026, 10, 27, tzinfo=UTC),
            missing_hard_skills=[MissingSkill("SQL", "hard"), MissingSkill("Docker", "hard")],
        )


class FakeYouTubeVideoSearchClient:
    async def search_videos(self, skill_name: str, max_results: int) -> list[YouTubeVideo]:
        assert max_results == 15
        return [
            YouTubeVideo(
                video_id=f"{skill_name}-{number}",
                title=f"{skill_name} video {number}",
                channel_title="PathBridge",
                description=None,
                url=f"https://www.youtube.com/watch?v={skill_name}-{number}",
                thumbnail_url=None,
            )
            for number in range(1, 5)
        ]


@pytest.mark.asyncio
async def test_recommends_at_most_three_videos_for_each_missing_skill() -> None:
    service = DefaultLearningPathRecommendationService(FakeGapAnalysisClient(), FakeYouTubeVideoSearchClient())

    recommendation = await service.recommend(7, 44)

    assert recommendation.gap_report_id == 9
    assert [item.position for item in recommendation.recommendations] == [1, 2, 3, 4, 5, 6]
    assert [item.skill_name for item in recommendation.recommendations] == ["SQL", "SQL", "SQL", "Docker", "Docker", "Docker"]


class JavaGapAnalysisClient:
    async def get_report(self, user_id: int, job_id: int) -> GapAnalysisReport:
        return GapAnalysisReport(
            id=9,
            job_id=44,
            updated_at=datetime(2026, 10, 27, tzinfo=UTC),
            missing_hard_skills=[MissingSkill("Java", "hard")],
        )


class JavaLearningVideoSearchClient:
    def __init__(self) -> None:
        self.query: str | None = None

    async def search_videos(self, query: str, max_results: int) -> list[YouTubeVideo]:
        self.query = query
        assert max_results == 15
        return [
            YouTubeVideo(
                video_id="minecraft-java",
                title="Minecraft Java vs Bedrock",
                channel_title="Zecto",
                description="Java vs Bedrock Minecraft.",
                url="https://www.youtube.com/watch?v=minecraft-java",
                thumbnail_url=None,
            ),
            YouTubeVideo(
                video_id="java-full-course",
                title="Java Full Course for Beginners",
                channel_title="Programming Academy",
                description="Learn Java fundamentals.",
                url="https://www.youtube.com/watch?v=java-full-course",
                thumbnail_url=None,
            ),
            YouTubeVideo(
                video_id="java-tutorial",
                title="Tutorial de Java desde cero",
                channel_title="Código Fácil",
                description="Curso para principiantes.",
                url="https://www.youtube.com/watch?v=java-tutorial",
                thumbnail_url=None,
            ),
            YouTubeVideo(
                video_id="java-spanish-course",
                title="Curso completo de Java",
                channel_title="Aprende Programación",
                description="Programación Java.",
                url="https://www.youtube.com/watch?v=java-spanish-course",
                thumbnail_url=None,
            ),
        ]


@pytest.mark.asyncio
async def test_queries_for_a_complete_course_and_excludes_irrelevant_java_videos() -> None:
    video_client = JavaLearningVideoSearchClient()
    service = DefaultLearningPathRecommendationService(JavaGapAnalysisClient(), video_client)

    recommendation = await service.recommend(7, 44)

    assert video_client.query == "Curso completo de Java"
    assert [item.video.video_id for item in recommendation.recommendations] == [
        "java-spanish-course",
        "java-full-course",
        "java-tutorial",
    ]
