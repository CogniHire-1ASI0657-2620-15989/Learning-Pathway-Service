from pathlib import Path

from pytest_bdd import given, parsers, scenarios, then, when

from conftest import build_path, headers

scenarios(str(Path(__file__).parent / "features" / "learning_pathway_progress_tracking.feature"))


@given(parsers.re(r"pathway (?P<path_id>\d+) of candidate (?P<user>\d+) has (?P<total>\d+) courses "
                  r"and (?P<done>\d+) of them are completed"))
def pathway_with_progress(world, path_id, user, total, done):
    skills = [f"Skill{i}" for i in range(int(total))]
    world.paths.paths[int(path_id)] = build_path(int(user), 50, skills, watched=int(done), path_id=int(path_id))


@when(parsers.re(r'a GET request is sent to "(?P<path>[^"]+)" as candidate (?P<user>\d+)'), target_fixture="response")
def get_progress(client, path, user):
    return client.get(path, headers=headers(int(user)))


@when(parsers.re(r"the candidate marks course (?P<item>\d+) of pathway (?P<path_id>\d+) as completed "
                 r"as candidate (?P<user>\d+)"), target_fixture="response")
def mark_watched(client, item, path_id, user):
    return client.patch(f"/api/v1/learning-paths/{path_id}/items/{item}", headers=headers(int(user)))


@then(parsers.re(r"the progress shows (?P<done>\d+) of (?P<total>\d+) courses completed with (?P<pct>\d+)%"))
def progress_shows(response, done, total, pct):
    body = response.json()
    assert (body["watched_items"], body["total_items"], body["progress_percentage"]) == (int(done), int(total), int(pct))


@then(parsers.re(r"the response progress is (?P<pct>\d+)%"))
def response_progress(response, pct):
    assert response.json()["progress_percentage"] == int(pct)


@then(parsers.re(r'the pathway status is "(?P<status>[^"]+)"'))
def pathway_status(response, status):
    assert response.json()["status"] == status
