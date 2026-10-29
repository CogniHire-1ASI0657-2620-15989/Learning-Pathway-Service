import httpx

from app.application.ports.youtube_video_search_client import YouTubeVideo, YouTubeVideoSearchClient


class YouTubeDataApiClient(YouTubeVideoSearchClient):
    _SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

    def __init__(self, api_key: str):
        self._api_key = api_key

    async def search_videos(self, skill_name: str, max_results: int) -> list[YouTubeVideo]:
        if max_results < 1 or max_results > 50:
            raise ValueError("max_results must be between 1 and 50.")
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(3.0)) as client:
                response = await client.get(
                    self._SEARCH_URL,
                    params={
                        "part": "snippet",
                        "type": "video",
                        "q": skill_name,
                        "maxResults": max_results,
                        "videoDuration": "long",
                        "relevanceLanguage": "es",
                        "key": self._api_key,
                    },
                )
            response.raise_for_status()
            body = response.json()
        except httpx.HTTPError as exc:
            raise RuntimeError("YouTube Data API is unavailable.") from exc

        videos: list[YouTubeVideo] = []
        for item in body.get("items") or []:
            video_id = (item.get("id") or {}).get("videoId")
            snippet = item.get("snippet") or {}
            if not video_id or not snippet.get("title"):
                continue
            thumbnails = snippet.get("thumbnails") or {}
            thumbnail = thumbnails.get("high") or thumbnails.get("medium") or thumbnails.get("default") or {}
            videos.append(
                YouTubeVideo(
                    video_id=str(video_id),
                    title=str(snippet["title"]),
                    channel_title=str(snippet.get("channelTitle") or ""),
                    description=str(snippet["description"]) if snippet.get("description") else None,
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    thumbnail_url=str(thumbnail["url"]) if thumbnail.get("url") else None,
                )
            )
        return videos
