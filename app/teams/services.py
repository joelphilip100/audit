from typing import Type

from sqlalchemy.orm import Session
from app.teams import models as team_models
from app.teams.repository import team_repo
from app.loggers import logger
from app.exceptions import TeamNotFoundException
from app.teams.models import Team
from app.teams import team_util


def create_team(team_name: str, db: Session) -> team_models.Team:
    team_util.ensure_team_name_is_unique(team_name, db)
    new_team = team_models.Team(team_name=team_name)
    return team_repo.create(new_team, db)


def get_all_teams(db: Session) -> list[Type[Team]]:
    return team_repo.get_all(db)


def get_team(team_id: int, db: Session) -> team_models.Team:
    team = team_repo.get_by_field("team_id", team_id, db)
    if not team:
        logger.warning(f"Team with ID {team_id} not found")
        raise TeamNotFoundException(team_id)
    return team


def update_team(team_id: int, team_name: str, db: Session) -> team_models.Team:
    team = get_team(team_id, db)
    team_util.ensure_team_name_is_unique(team_name, db, team.team_id)
    team.team_name = team_name
    return team_repo.update(team, db)


def delete_team(team_id: int, db: Session) -> None:
    team = get_team(team_id, db)
    team_repo.delete(team, db)
