from pathlib import Path

from pytest_bdd import parsers, scenarios, then

scenarios(str(Path(__file__).parent / "features" / "certificate_automatic_validation.feature"))


@then(parsers.re(r'the skill "(?P<skill>[^"]+)" is registered as verified in the candidate profile'))
def skill_verified(response, world, ctx, skill):
    assert (ctx["user"], skill) in world.identity.verified_skills
    assert response.json()["profile_sync_status"] == "synchronized"


@then(parsers.re(r"the gap report of job (?P<job>\d+) is recalculated"))
def gap_recalculated(response, world, ctx, job):
    assert (ctx["user"], int(job)) in world.gap.regenerated
    assert response.json()["gap_refresh_status"] == "synchronized"


@then("no skill is registered as verified in the candidate profile")
def no_skill_verified(response, world):
    assert world.identity.verified_skills == []
    assert response.json()["profile_sync_status"] == "not_required"
