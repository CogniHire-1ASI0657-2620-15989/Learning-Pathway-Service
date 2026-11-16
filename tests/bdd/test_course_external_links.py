from pathlib import Path

from pytest_bdd import parsers, scenarios, then, when

from conftest import headers

scenarios(str(Path(__file__).parent / "features" / "course_external_links.feature"))


@when(parsers.re(r'a GET request is sent to "(?P<path>[^"]+)" as candidate (?P<user>\d+)'), target_fixture="response")
def get_pathway(client, path, user):
    return client.get(path, headers=headers(int(user)))


@then(parsers.re(r'every course in the pathway has an external "(?P<prefix>[^"]+)" link'))
def external_links(response, prefix):
    items = response.json()["items"]
    assert items and all(item["video_url"].startswith(prefix) for item in items)
