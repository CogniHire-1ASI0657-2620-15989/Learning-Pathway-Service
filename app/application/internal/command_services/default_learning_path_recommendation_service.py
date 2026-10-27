from dataclasses import dataclass
from datetime import datetime

from app.application.ports.gap_analysis_client import GapAnalysisClient
from app.application.ports.youtube_video_search_client import YouTubeVideo, YouTubeVideoSearchClient


@dataclass(frozen=True)
class VideoRecommendation:
    position: int
    skill_name: str
    skill_type: str
    video: YouTubeVideo


@dataclass(frozen=True)
class LearningPathRecommendation:
    gap_report_id: int
    gap_report_updated_at: datetime
    recommendations: list[VideoRecommendation]


class DefaultLearningPathRecommendationService:
    VIDEOS_PER_SKILL = 3

    def __init__(self, gap_analysis_client: GapAnalysisClient, youtube_video_search_client: YouTubeVideoSearchClient):
        self._gap_analysis_client = gap_analysis_client
        self._youtube_video_search_client = youtube_video_search_client

    async def recommend(self, user_id: int, job_id: int) -> LearningPathRecommendation:
        report = await self._gap_analysis_client.get_report(user_id, job_id)
        recommendations: list[VideoRecommendation] = []

        for skill in report.missing_hard_skills:
            videos = await self._youtube_video_search_client.search_videos(skill.name, self.VIDEOS_PER_SKILL)
            first_position = len(recommendations) + 1
            recommendations.extend(
                VideoRecommendation(
                    position=first_position + offset,
                    skill_name=skill.name,
                    skill_type=skill.skill_type,
                    video=video,
                )
                for offset, video in enumerate(videos[: self.VIDEOS_PER_SKILL])
            )

        return LearningPathRecommendation(
            gap_report_id=report.id,
            gap_report_updated_at=report.updated_at,
            recommendations=recommendations,
        )
