"""Soporte común de los tests BDD del Learning Pathway Service (ningún archivo de app/ se modifica).

El microservicio se prueba por su API HTTP real (/api/v1/learning-paths y /api/v1/certificates)
con los servicios de aplicación y el dominio reales. Solo se sustituyen por fakes en memoria los
puertos que salen del proceso: PostgreSQL (repositorios), Gap Analysis, YouTube, OCR e Identity.
Cada fake es configurable por escenario a través del fixture `world`.
"""
import os
from datetime import datetime, timezone
from types import SimpleNamespace

for key, value in {"DATABASE_URL": "sqlite+aiosqlite://", "IDENTITY_SERVICE_URL": "http://identity.test",
                   "GAP_ANALYSIS_SERVICE_URL": "http://gap.test", "YOUTUBE_DATA_API_KEY": "x",
                   "GATEWAY_USER_ID_HEADER": "X-User-Id", "INTERNAL_API_KEY": "test-key"}.items():
    os.environ[key] = value
os.environ.pop("REDIS_URL", None)  # el cache nunca debe apuntar a un Redis real durante los tests

import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, then, when

from app.application.internal.command_services.default_certificate_command_service import DefaultCertificateCommandService
from app.application.internal.command_services.default_certificate_validation_service import DefaultCertificateValidationService
from app.application.internal.command_services.default_learning_path_command_service import DefaultLearningPathCommandService
from app.application.internal.command_services.default_learning_path_recommendation_service import DefaultLearningPathRecommendationService
from app.application.internal.query_service.default_certificate_query_service import DefaultCertificateQueryService
from app.application.internal.query_service.default_learning_path_query_service import DefaultLearningPathQueryService
from app.application.ports.gap_analysis_client import GapAnalysisReport, MissingSkill
from app.application.ports.identity_profile_client import UserProfile
from app.application.ports.youtube_video_search_client import YouTubeVideo
from app.dependencies import get_db_session
from app.domain.model.aggregates.learning_path import LearningPath
from app.domain.model.entities.learning_path_item import LearningPathItem
from app.domain.model.value_objects.learning_path_item_status import LearningPathItemStatus
from app.domain.model.value_objects.learning_path_status import LearningPathStatus
from app.interfaces.rest.controller import certificate_controller, learning_path_controller
from app.main import app

NOW = datetime(2026, 10, 27, tzinfo=timezone.utc)
PROFILE_NAME = "Ana Perez"
VALID_PDF = b"%PDF-1.4\n% diploma de prueba\n"


def headers(user_id: int) -> dict:
    return {"X-User-Id": str(user_id), "X-Internal-Api-Key": "test-key"}


def build_path(user_id: int, job_id: int, skills: list[str], watched: int = 0, path_id: int | None = None) -> LearningPath:
    """Ruta con un video por habilidad; los primeros `watched` videos ya vistos."""
    items = [
        LearningPathItem(i, path_id, i, skill, "hard", f"vid-{i}", f"Curso completo de {skill}", "Canal", None,
                         f"https://www.youtube.com/watch?v=vid-{i}", None,
                         LearningPathItemStatus.WATCHED if i <= watched else LearningPathItemStatus.PENDING,
                         NOW if i <= watched else None, NOW, NOW)
        for i, skill in enumerate(skills, start=1)
    ]
    path = LearningPath(path_id, user_id, job_id, 1, NOW, LearningPathStatus.ACTIVE, 0, NOW, NOW, items)
    path.recalculate_progress(NOW)
    return path


# ---------- Fakes de los puertos externos ----------
class FakeGapClient:
    def __init__(self):
        self.reports: dict[tuple[int, int], list[str]] = {}
        self.regenerated: list[tuple[int, int]] = []

    async def get_report(self, user_id, job_id):
        if (user_id, job_id) not in self.reports:
            raise ValueError("Gap report not found.")
        skills = self.reports[(user_id, job_id)]
        return GapAnalysisReport(1, job_id, NOW, [MissingSkill(name, "hard") for name in skills])

    async def regenerate_report(self, user_id, job_id):
        self.regenerated.append((user_id, job_id))
        return await self.get_report(user_id, job_id)


class FakeYouTube:
    def __init__(self):
        self.queries: list[str] = []

    async def search_videos(self, query, max_results):
        self.queries.append(query)
        skill = query.replace("Curso completo de ", "")
        return [YouTubeVideo(f"{skill.lower()}-{n}", f"Curso completo de {skill} desde cero #{n}", "Canal", None,
                             f"https://www.youtube.com/watch?v={skill.lower()}-{n}", None) for n in range(5)]


class FakeOcr:
    """Simula el extractor OCR: devuelve el texto que el escenario defina."""

    def __init__(self):
        self.text = ""

    async def extract_text(self, content, content_type):
        return self.text


class FakeIdentity:
    """Simula Identity Service: perfil del usuario y registro de habilidades verificadas."""

    def __init__(self):
        self.available = True
        self.verified_skills: list[tuple[int, str]] = []

    async def get_user_profile(self, user_id):
        return UserProfile(user_id, PROFILE_NAME)

    async def ensure_verified_hard_skill(self, user_id, skill_name):
        if not self.available:
            raise RuntimeError("Identity Service is unavailable.")
        self.verified_skills.append((user_id, skill_name))


class FakePathRepo:
    def __init__(self):
        self.paths: dict[int, LearningPath] = {}

    async def upsert(self, path):
        if path.id is None:
            path.id = max(self.paths, default=0) + 1
            for i, item in enumerate(path.items, start=1):
                item.id, item.learning_path_id = i, path.id
        self.paths[path.id] = path
        return path

    async def find_by_user_and_job(self, user_id, job_id):
        return next((p for p in self.paths.values() if (p.user_id, p.job_id) == (user_id, job_id)), None)

    async def find_by_id_and_user(self, path_id, user_id):
        path = self.paths.get(path_id)
        return path if path and path.user_id == user_id else None


class FakeCertificateRepo:
    def __init__(self):
        self.items = {}

    async def upsert(self, certificate):
        if certificate.id is None:
            certificate.id = len(self.items) + 1
        self.items[certificate.id] = certificate
        return certificate

    async def find_by_id_and_user(self, certificate_id, user_id):
        cert = self.items.get(certificate_id)
        return cert if cert and cert.user_id == user_id else None

    async def list_by_user(self, user_id, learning_path_id=None):
        return [c for c in self.items.values()
                if c.user_id == user_id and (learning_path_id is None or c.learning_path_id == learning_path_id)]


@pytest.fixture
def world():
    return SimpleNamespace(gap=FakeGapClient(), youtube=FakeYouTube(), ocr=FakeOcr(), identity=FakeIdentity(),
                           paths=FakePathRepo(), certificates=FakeCertificateRepo())


@pytest.fixture
def ctx():
    """Estado compartido entre los steps de un escenario."""
    return {}


@pytest.fixture
def client(world, monkeypatch):
    from app.infrastructure.configuration.settings import get_settings
    get_settings.cache_clear()

    async def commit(): ...

    async def fake_session():
        yield None

    recommendation = DefaultLearningPathRecommendationService(world.gap, world.youtube)
    validation = DefaultCertificateValidationService(world.ocr, world.identity)
    app.dependency_overrides[get_db_session] = fake_session
    monkeypatch.setattr(learning_path_controller, "get_learning_path_command_service",
                        lambda s: DefaultLearningPathCommandService(recommendation, world.paths, commit))
    monkeypatch.setattr(learning_path_controller, "get_learning_path_query_service",
                        lambda s: DefaultLearningPathQueryService(world.paths))
    monkeypatch.setattr(certificate_controller, "get_certificate_command_service",
                        lambda s: DefaultCertificateCommandService(validation, world.certificates, world.paths,
                                                                   world.identity, world.gap, commit))
    monkeypatch.setattr(certificate_controller, "get_certificate_query_service",
                        lambda s: DefaultCertificateQueryService(world.certificates))
    yield TestClient(app)
    app.dependency_overrides.clear()
    get_settings.cache_clear()


def upload_certificate(client, user_id: int, path_id: int, skill: str, content: bytes = VALID_PDF,
                       content_type: str = "application/pdf", filename: str = "diploma.pdf"):
    return client.post("/api/v1/certificates",
                       data={"learning_path_id": str(path_id), "skill_name": skill},
                       files={"file": (filename, content, content_type)},
                       headers=headers(user_id))


# ---------- Steps compartidos ----------
@given(parsers.re(r'candidate (?P<user>\d+) has an identified skill gap in "(?P<skill>[^"]+)" for job (?P<job>\d+)'))
def candidate_with_gap(world, user, skill, job):
    world.gap.reports[(int(user), int(job))] = [skill]


@given(parsers.re(r"candidate (?P<user>\d+) already generated the pathway for job (?P<job>\d+)"))
def already_generated(client, user, job):
    assert client.post("/api/v1/learning-paths", json={"job_id": int(job)}, headers=headers(int(user))).status_code == 201


@given(parsers.re(r'candidate (?P<user>\d+) has an active learning pathway (?P<path_id>\d+) for job (?P<job>\d+) '
                  r'that includes the skill "(?P<skill>[^"]+)"'))
def active_pathway(world, ctx, user, path_id, job, skill):
    ctx["user"], ctx["path_id"], ctx["job"] = int(user), int(path_id), int(job)
    world.paths.paths[int(path_id)] = build_path(int(user), int(job), [skill], path_id=int(path_id))
    world.gap.reports[(int(user), int(job))] = [skill]


@given(parsers.re(r'the OCR reads the text "(?P<text>[^"]*)" from the diploma'))
def ocr_reads(world, text):
    world.ocr.text = text


@when(parsers.re(r'the candidate uploads a valid PDF diploma for skill "(?P<skill>[^"]+)" to "/api/v1/certificates"'),
      target_fixture="response")
def upload_valid_pdf(client, ctx, skill):
    response = upload_certificate(client, ctx["user"], ctx["path_id"], skill)
    ctx["certificate"] = response.json()
    return response


@then(parsers.re(r"the response status is (?P<code>\d+) .+"))
def status_is(response, code):
    assert response.status_code == int(code), response.text


@then(parsers.re(r'the response body contains the message "(?P<message>[^"]+)"'))
def message_is(response, message):
    assert message in str(response.json().get("detail"))


@then(parsers.re(r'the certificate status is "(?P<status>[^"]+)"'))
def certificate_status(response, status):
    assert response.json()["status"] == status


@then(parsers.re(r'the certificate validation detail is "(?P<detail>[^"]+)"'))
def certificate_detail(response, detail):
    assert response.json()["validation_detail"] == detail
