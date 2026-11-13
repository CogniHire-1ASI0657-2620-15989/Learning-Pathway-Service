import httpx

from app.application.ports.youtube_video_search_client import YouTubeVideo, YouTubeVideoSearchClient
from app.observability import outbound_headers
from app.infrastructure.cache.redis_json_cache import RedisJsonCache
from app.infrastructure.resilience.circuit_breaker import CircuitBreaker


class YouTubeDataApiClient(YouTubeVideoSearchClient):
    _SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

    def __init__(
        self,
        api_key: str,
        cache: RedisJsonCache | None = None,
        breaker: CircuitBreaker | None = None,
    ):
        self._api_key = api_key
        self._cache = cache or RedisJsonCache(None)
        self._breaker = breaker or CircuitBreaker()

    async def search_videos(self, skill_name: str, max_results: int) -> list[YouTubeVideo]:
        if max_results < 1 or max_results > 50:
            raise ValueError("max_results must be between 1 and 50.")
        cache_key = f"learning-pathway:v1:youtube:{skill_name.casefold()}:{max_results}"
        cached = await self._cache.get(cache_key)
        if cached is not None:
            try:
                return [YouTubeVideo(**video) for video in cached]
            except (KeyError, TypeError):
                await self._cache.delete(cache_key)
        if not self._breaker.allow_request():
            raise RuntimeError("YouTube circuit breaker is open.")
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(3.0)) as client:
                response = await client.get(
                    self._SEARCH_URL,
                    headers=outbound_headers(),
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
            self._breaker.record_failure()
            raise RuntimeError("YouTube Data API is unavailable.") from exc
        self._breaker.record_success()

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
        await self._cache.set(cache_key, [video.__dict__ for video in videos], ttl_seconds=21600)
        return videos
