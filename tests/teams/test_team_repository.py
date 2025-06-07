import pytest

from sqlalchemy.exc import IntegrityError, InvalidRequestError
from app.teams.repository import team_repo
from app.teams import models as team_models


def test_get_all_teams_empty(test_db):
    teams = team_repo.get_all(test_db)
    assert len(teams) == 0


def test_create_team(test_db):
    team_name = "TEAM_CT1"
    team = team_models.Team(team_name=team_name)

    new_team = team_repo.create(team, test_db)

    assert new_team.team_name == team.team_name
    assert new_team.team_id is not None


def test_create_team_with_duplicate_name(test_db):
    team_name = "TEAM_CT2"
    team = team_models.Team(team_name=team_name)
    team_repo.create(team, test_db)

    team = team_models.Team(team_name=team_name)
    with pytest.raises(IntegrityError) as exc_info:
        team_repo.create(team, test_db)

    assert "UNIQUE constraint failed: teams.team_name" in str(exc_info.value)


def test_create_team_with_team_name_missing(test_db):
    team = team_models.Team(team_name=None)
    with pytest.raises(IntegrityError) as exc_info:
        team_repo.create(team, test_db)

    assert "NOT NULL constraint failed: teams.team_name" in str(exc_info.value)


def test_get_team_by_name(test_db):
    team_name = "TEAM_GT1"
    team = team_models.Team(team_name=team_name)
    team_repo.create(team, test_db)

    team = team_repo.get_team_by_name(team_name, test_db)

    assert team.team_name == team_name
    assert team.team_id is not None


def test_get_all_teams(test_db):
    team1 = team_models.Team(team_name="TEAM_GT2")
    team2 = team_models.Team(team_name="TEAM_GT3")
    new_team1 = team_repo.create(team1, test_db)
    new_team2 = team_repo.create(team2, test_db)

    teams = team_repo.get_all(test_db)

    assert len(teams) >= 2
    assert any(team.team_name == new_team1.team_name for team in teams)
    assert any(team.team_name == new_team2.team_name for team in teams)


def test_get_team_by_name_not_found(test_db):
    team_name = "TEAM_GT4"
    team = team_repo.get_team_by_name(team_name, test_db)

    assert team is None


def test_update_team_name(test_db):
    team_name = "TEAM_UT1"
    team_model = team_models.Team(team_name=team_name)
    team = team_repo.create(team_model, test_db)

    team.team_name = "TEAM_UT2"
    updated_team = team_repo.update(team, test_db)

    assert updated_team.team_name == "TEAM_UT2"


def test_update_team_name_conflict(test_db):
    team_repo.create(team_models.Team(team_name="TeamA"), test_db)
    team2 = team_repo.create(team_models.Team(team_name="TeamB"), test_db)

    team2.team_name = "TeamA"

    with pytest.raises(IntegrityError) as exc_info:
        team_repo.update(team2, test_db)

    assert "UNIQUE constraint failed: teams.team_name" in str(exc_info.value)


def test_delete_team(test_db):
    team_name = "TEAM_DT1"
    team_model = team_models.Team(team_name=team_name)
    new_team = team_repo.create(team_model, test_db)

    team = team_repo.get_by_field("team_id", new_team.team_id, test_db)

    team_repo.delete(team, test_db)

    team = team_repo.get_by_field("team_id", new_team.team_id, test_db)

    assert team is None


def test_delete_team_not_found(test_db):
    team = team_models.Team(team_name="TEAM_DT2")
    with pytest.raises(InvalidRequestError):
        team_repo.delete(team, test_db)
