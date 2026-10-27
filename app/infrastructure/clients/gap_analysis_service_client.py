from datetime import datetime

import httpx

from app.application.ports.gap_analysis_client import GapAnalysisClient, GapAnalysisReport, MissingSkill


class GapAnalysisServiceClient(GapAnalysisClient):
    def __init__(self, base_url: str, user_id_header: str):
        self._base_url = base_url.rstrip("/")
        self._user_id_header = user_id_header

    async def get_report(self, user_id: int, job_id: int) -> GapAnalysisReport:
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(3.0)) as client:
                response = await client.get(
                    f"{self._base_url}/api/v1/gap-reports/{job_id}",
                    headers={self._user_id_header: str(user_id)},
                )
            if response.status_code == 404:
                raise ValueError("Gap report not found.")
            response.raise_for_status()
            body = response.json()
        except httpx.HTTPError as exc:
            raise RuntimeError("Gap Analysis Service is unavailable.") from exc

        return self._to_report(body)

    async def regenerate_report(self, user_id: int, job_id: int) -> GapAnalysisReport:
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
                response = await client.post(
                    f"{self._base_url}/api/v1/gap-reports",
                    headers={self._user_id_header: str(user_id)},
                    json={"job_id": job_id},
                )
            if response.status_code == 404:
                raise ValueError("Job or user profile not found for gap report regeneration.")
            response.raise_for_status()
            body = response.json()
        except httpx.HTTPError as exc:
            raise RuntimeError("Gap Analysis Service is unavailable.") from exc

        return self._to_report(body)

    @staticmethod
    def _to_report(body: dict) -> GapAnalysisReport:
        return GapAnalysisReport(
            id=int(body["id"]),
            job_id=int(body["job_id"]),
            updated_at=datetime.fromisoformat(str(body["updated_at"]).replace("Z", "+00:00")),
            missing_hard_skills=[
                MissingSkill(name=str(skill["name"]), skill_type=str(skill["skill_type"]))
                for skill in body.get("missing_hard_skills") or []
            ],
        )
