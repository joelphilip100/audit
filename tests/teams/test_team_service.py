import pytest
from pydantic import ValidationError

from app.teams import services as team_services
from app.teams import schemas as team_schema
from app.exceptions import TeamNotFoundException, TeamNameExistsException

SCHEMAS = [team_schema.TeamCreateRequest, team_schema.TeamUpdateRequest]


def test_get_all_teams_empty(test_db):
    teams = team_services.get_all_teams(test_db)
    assert len(teams) == 0


def test_create_team(test_db):
    team_name = "TEAM_CTS1"
    team = team_services.create_team(team_name, test_db)

    assert team.team_id is not None
    assert team.team_name == "TEAM_CTS1"


def test_create_team_with_existing_name(test_db):
    team_name = "TEAM_CTS2"
    team_services.create_team(team_name, test_db)

    with pytest.raises(TeamNameExistsException) as exc_info:
        team_services.create_team(team_name, test_db)

    assert f"Team {team_name} already exists" in str(exc_info.value)


def test_get_all_teams(test_db):
    team_services.create_team("TEAM_RTS1", test_db)
    team_services.create_team("TEAM_RTS2", test_db)
    team_services.create_team("TEAM_RTS3", test_db)

    teams = team_services.get_all_teams(test_db)

    assert any(team.team_name == "TEAM_RTS1" for team in teams)
    assert any(team.team_name == "TEAM_RTS2" for team in teams)
    assert any(team.team_name == "TEAM_RTS3" for team in teams)


def test_get_team_by_id(test_db):
    team_name = "TEAM_RTS4"
    new_team = team_services.create_team(team_name, test_db)

    team = team_services.get_team(new_team.team_id, test_db)

    assert team.team_name == team_name


def test_get_team_by_id_not_found(test_db):
    team_id = 1000

    with pytest.raises(TeamNotFoundException) as exc_info:
        team_services.get_team(team_id, test_db)

    assert f"Team with ID {team_id} not found" in str(exc_info.value)


def test_update_team(test_db):
    team_name = "TEAM_UTS1"
    updated_team_name = "TEAM_UTS2"
    team = team_services.create_team(team_name, test_db)

    updated_team = team_services.update_team(team.team_id, updated_team_name, test_db)

    assert updated_team.team_id == team.team_id
    assert updated_team.team_name == updated_team_name


def test_update_team_no_changes(test_db):
    team_name = "TEAM_UTS3"
    team = team_services.create_team(team_name, test_db)

    updated_team = team_services.update_team(team.team_id, team_name, test_db)

    assert updated_team.team_id == team.team_id
    assert updated_team.team_name == team_name


def test_update_team_with_team_id_not_found(test_db):
    team_id = 1000
    updated_team_name = "TEAM_UTS4"

    with pytest.raises(TeamNotFoundException) as exc_info:
        team_services.update_team(team_id, updated_team_name, test_db)

    assert f"Team with ID {team_id} not found" in str(exc_info.value)


def test_delete_team(test_db):
    team_name = "TEAM_DTS1"
    team = team_services.create_team(team_name, test_db)

    team_services.delete_team(team.team_id, test_db)

    with pytest.raises(TeamNotFoundException) as exc_info:
        team_services.get_team(team.team_id, test_db)

    assert f"Team with ID {team.team_id} not found" in str(exc_info.value)


def test_delete_team_not_found(test_db):
    team_id = 1000

    with pytest.raises(TeamNotFoundException) as exc_info:
        team_services.delete_team(team_id, test_db)

    assert f"Team with ID {team_id} not found" in str(exc_info.value)


def test_recreate_team_after_deletion(test_db):
    team_name = "TEAM_RTS5"
    team = team_services.create_team(team_name, test_db)

    team_services.delete_team(team.team_id, test_db)

    response = team_services.create_team(team_name, test_db)

    assert response.team_name == team_name
    assert response.team_id is not None


# Schema tests

@pytest.mark.parametrize("schemas", SCHEMAS)
def test_team_name_is_converted_to_uppercase(schemas):
    request = schemas(
        team_name="team_one"
    )

    assert request.team_name == "TEAM_ONE"


def test_create_request_without_fields():
    with pytest.raises(ValidationError) as exc_info:
        team_schema.TeamCreateRequest()

    assert "1 validation error for TeamCreateRequest\nteam_name" in str(exc_info.value)


def test_update_request_without_fields():
    with pytest.raises(ValidationError) as exc_info:
        team_schema.TeamUpdateRequest()

    assert "1 validation error for TeamUpdateRequest\nteam_name" in str(exc_info.value)


@pytest.mark.parametrize("schemas", SCHEMAS)
@pytest.mark.parametrize(
    "field_name, data, expected_message",
    [
        ("team_name", {"team_name": "a"}, "String should have at least 2 characters"),
        ("team_name", {"team_name": "a" * 21}, "String should have at most 20 characters"),
    ]
)
def test_create_update_request_field_length_validation(schemas, field_name, data, expected_message):
    with pytest.raises(ValidationError) as exc_info:
        schemas(**data)

    assert expected_message in str(exc_info.value)
