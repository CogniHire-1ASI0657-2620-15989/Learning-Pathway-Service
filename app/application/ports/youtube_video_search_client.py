from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class YouTubeVideo:
    video_id: str
    title: str
    channel_title: str
    description: str | None
    url: str
    thumbnail_url: str | None


class YouTubeVideoSearchClient(ABC):
    @abstractmethod
    async def search_videos(self, skill_name: str, max_results: int) -> list[YouTubeVideo]: ...
