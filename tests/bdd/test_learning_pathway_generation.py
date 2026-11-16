from pathlib import Path

from pytest_bdd import given, parsers, scenarios, then, when

from conftest import headers

scenarios(str(Path(__file__).parent / "features" / "learning_pathway_generation.feature"))


@given(parsers.re(r"candidate (?P<user>\d+) has 100% match with job (?P<job>\d+)"))
def candidate_without_gaps(world, user, job):
    world.gap.reports[(int(user), int(job))] = []


@given(parsers.re(r"candidate (?P<user>\d+) has no gap report for job (?P<job>\d+)"))
def candidate_without_report(world, user, job):
    world.gap.reports.pop((int(user), int(job)), None)


@when(parsers.re(r'a POST request is sent to "/api/v1/learning-paths" with job_id (?P<job>\d+) as candidate (?P<user>\d+)'),
      target_fixture="response")
def generate(client, job, user):
    return client.post("/api/v1/learning-paths", json={"job_id": int(job)}, headers=headers(int(user)))


@then(parsers.re(r'the response body contains (?P<count>\d+) recommended courses targeting "(?P<skill>[^"]+)"'))
def courses_for_skill(response, count, skill):
    items = response.json()["items"]
    assert len(items) == int(count)
    assert all(item["skill_name"] == skill and item["status"] == "pending" for item in items)


@then("the response body contains no recommended courses")
def no_courses(response):
    assert response.json()["items"] == []


@then(parsers.re(r"the learning pathway progress is (?P<pct>\d+)%"))
def progress(response, pct):
    assert response.json()["progress_percentage"] == int(pct)


@then("the course catalog was searched only once")
def searched_once(world):
    assert len(world.youtube.queries) == 1
