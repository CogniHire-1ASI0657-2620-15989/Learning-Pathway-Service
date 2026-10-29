from dataclasses import dataclass
from datetime import datetime
import re
import unicodedata

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
    CANDIDATES_PER_SKILL = 15
    _LEARNING_MARKERS = (
        "curso completo",
        "curso",
        "tutorial",
        "aprende",
        "aprenda",
        "desde cero",
        "principiantes",
        "programacion",
        "programming",
        "learn",
        "full course",
        "for beginners",
    )
    _IRRELEVANT_CONTEXT_MARKERS = (
        "minecraft",
        "bedrock",
        "gameplay",
        "survival",
    )

    def __init__(self, gap_analysis_client: GapAnalysisClient, youtube_video_search_client: YouTubeVideoSearchClient):
        self._gap_analysis_client = gap_analysis_client
        self._youtube_video_search_client = youtube_video_search_client

    async def recommend(self, user_id: int, job_id: int) -> LearningPathRecommendation:
        report = await self._gap_analysis_client.get_report(user_id, job_id)
        recommendations: list[VideoRecommendation] = []

        for skill in report.missing_hard_skills:
            query = f"Curso completo de {skill.name}"
            candidates = await self._youtube_video_search_client.search_videos(query, self.CANDIDATES_PER_SKILL)
            videos = self._select_learning_videos(skill.name, candidates)
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

    @classmethod
    def _select_learning_videos(cls, skill_name: str, candidates: list[YouTubeVideo]) -> list[YouTubeVideo]:
        ranked_videos: list[tuple[int, int, YouTubeVideo]] = []
        for index, video in enumerate(candidates):
            title = cls._normalize(video.title)
            description = cls._normalize(video.description or "")
            combined_text = f"{title} {description}"
            if not cls._mentions_skill(title, skill_name):
                continue
            if any(cls._contains_phrase(combined_text, marker) for marker in cls._IRRELEVANT_CONTEXT_MARKERS):
                continue

            title_marker_count = sum(cls._contains_phrase(title, marker) for marker in cls._LEARNING_MARKERS)
            description_marker_count = sum(cls._contains_phrase(description, marker) for marker in cls._LEARNING_MARKERS)
            score = title_marker_count * 10 + description_marker_count * 2
            if cls._contains_phrase(title, "curso completo"):
                score += 12
            elif cls._contains_phrase(title, "full course"):
                score += 10
            if score == 0:
                continue
            ranked_videos.append((score, index, video))

        ranked_videos.sort(key=lambda item: (-item[0], item[1]))
        return [video for _, _, video in ranked_videos[: cls.VIDEOS_PER_SKILL]]

    @staticmethod
    def _mentions_skill(text: str, skill_name: str) -> bool:
        normalized_skill = DefaultLearningPathRecommendationService._normalize(skill_name)
        return bool(re.search(rf"(?<![a-z0-9]){re.escape(normalized_skill)}(?![a-z0-9])", text))

    @staticmethod
    def _contains_phrase(text: str, phrase: str) -> bool:
        return bool(re.search(rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9])", text))

    @staticmethod
    def _normalize(value: str) -> str:
        decomposed = unicodedata.normalize("NFKD", value)
        without_accents = "".join(character for character in decomposed if not unicodedata.combining(character))
        return re.sub(r"\s+", " ", without_accents).strip().casefold()
