import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    database_url: str
    identity_service_url: str
    gap_analysis_service_url: str
    youtube_data_api_key: str
    gateway_user_id_header: str


@lru_cache
def get_settings() -> Settings:
    values = {
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "IDENTITY_SERVICE_URL": os.getenv("IDENTITY_SERVICE_URL"),
        "GAP_ANALYSIS_SERVICE_URL": os.getenv("GAP_ANALYSIS_SERVICE_URL"),
        "YOUTUBE_DATA_API_KEY": os.getenv("YOUTUBE_DATA_API_KEY"),
        "GATEWAY_USER_ID_HEADER": os.getenv("GATEWAY_USER_ID_HEADER"),
    }
    missing = [name for name, value in values.items() if not value or not value.strip()]
    if missing:
        raise RuntimeError(f"Missing required configuration: {', '.join(missing)}")
    return Settings(
        database_url=values["DATABASE_URL"].strip(),
        identity_service_url=values["IDENTITY_SERVICE_URL"].rstrip("/"),
        gap_analysis_service_url=values["GAP_ANALYSIS_SERVICE_URL"].rstrip("/"),
        youtube_data_api_key=values["YOUTUBE_DATA_API_KEY"].strip(),
        gateway_user_id_header=values["GATEWAY_USER_ID_HEADER"].strip(),
    )
