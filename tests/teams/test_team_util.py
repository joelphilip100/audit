from unittest.mock import patch

import pytest

from app.exceptions import TeamNameExistsException
from app.teams.models import Team
from app.teams.team_util import ensure_team_name_is_unique


def test_unique_team_name_passes(fake_db):
    with patch("app.teams.team_util.team_repo.get_team_by_name", return_value=None):
        ensure_team_name_is_unique("Alpha", fake_db)


def test_same_team_name_same_id_passes(fake_db):
    existing_team = Team(team_id=1, team_name="Alpha")
    with patch("app.teams.team_util.team_repo.get_team_by_name", return_value=existing_team):
        ensure_team_name_is_unique("Alpha", fake_db, current_team_id=1)


def test_same_team_name_different_id_raises(fake_db):
    existing_team = Team(team_id=2, team_name="Alpha")
    with patch("app.teams.team_util.team_repo.get_team_by_name", return_value=existing_team):
        with pytest.raises(TeamNameExistsException) as exc:
            ensure_team_name_is_unique("Alpha", fake_db, current_team_id=1)

        assert "Team Alpha already exists" in str(exc.value)