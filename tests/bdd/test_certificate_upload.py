from pathlib import Path

from pytest_bdd import parsers, scenarios, then, when

from conftest import VALID_PDF, upload_certificate

scenarios(str(Path(__file__).parent / "features" / "certificate_upload.feature"))

SIX_MB = 6 * 1024 * 1024


@when(parsers.re(r'the candidate uploads a PDF diploma larger than 5 MB for skill "(?P<skill>[^"]+)"'),
      target_fixture="response")
def upload_oversized(client, ctx, skill):
    return upload_certificate(client, ctx["user"], ctx["path_id"], skill, content=VALID_PDF + b"0" * SIX_MB)


@when(parsers.re(r'the candidate uploads a "(?P<content_type>[^"]+)" file for skill "(?P<skill>[^"]+)"'),
      target_fixture="response")
def upload_wrong_type(client, ctx, content_type, skill):
    return upload_certificate(client, ctx["user"], ctx["path_id"], skill, content=b"no soy un diploma",
                              content_type=content_type, filename="diploma.txt")


@then(parsers.re(r'the certificate is registered for skill "(?P<skill>[^"]+)" in learning pathway (?P<path_id>\d+)'))
def registered(response, world, skill, path_id):
    body = response.json()
    assert body["skill_name"] == skill and body["learning_path_id"] == int(path_id)
    assert body["id"] in world.certificates.items
