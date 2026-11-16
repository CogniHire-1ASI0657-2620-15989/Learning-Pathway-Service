from pathlib import Path

from pytest_bdd import given, parsers, scenarios, then, when

from conftest import headers, upload_certificate

scenarios(str(Path(__file__).parent / "features" / "certificate_validation_error_handling.feature"))


@given(parsers.re(r'the candidate uploaded a diploma for skill "(?P<skill>[^"]+)"'))
def uploaded(client, ctx, skill):
    response = upload_certificate(client, ctx["user"], ctx["path_id"], skill)
    assert response.status_code == 201, response.text
    ctx["certificate"] = response.json()


@given("the Identity Service is unavailable")
def identity_down(world):
    world.identity.available = False


@given("the Identity Service becomes available again")
def identity_up(world, ctx):
    assert ctx["certificate"]["profile_sync_status"] == "failed"  # precondición: la primera sincronización falló
    world.identity.available = True


@when(parsers.re(r'the candidate requests the uploaded certificate from "(?P<path>[^"]+)"'), target_fixture="response")
def get_certificate(client, ctx, path):
    return client.get(path.format(id=ctx["certificate"]["id"]), headers=headers(ctx["user"]))


@when(parsers.re(r'the candidate retries the synchronization at "(?P<path>[^"]+)"'), target_fixture="response")
def retry_sync(client, ctx, path):
    return client.post(path.format(id=ctx["certificate"]["id"]), headers=headers(ctx["user"]))


@then(parsers.re(r'the certificate profile synchronization status is "(?P<status>[^"]+)"'))
def profile_sync(response, status):
    assert response.json()["profile_sync_status"] == status
