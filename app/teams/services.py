from sqlalchemy.orm import Session
from app.teams import models as team_models
from app.teams import repository
from app.loggers import logger
from app.exceptions import TeamNameExistsException, TeamNotFoundException

def create_team(team_name: str, db: Session) -> team_models.Team:
    ensure_team_name_is_unique(team_name, db)
    new_team = team_models.Team(team_name=team_name)
    return repository.create_team(new_team, db)

def get_all_teams(db: Session) -> list[team_models.Team]:
    return repository.get_all_teams(db)

def get_team(team_id: int, db) -> team_models.Team:
    team = repository.get_team_by_id(team_id, db)
    if not team:
        logger.warning(f"Team with ID {team_id} not found")
        raise TeamNotFoundException(team_id)
    return team

def update_team(team_id: int, team_name: str, db: Session) -> team_models.Team:
    team = get_team(team_id, db)
    ensure_team_name_is_unique(team_name, db)
    team.team_name = team_name
    return repository.update_team_name(team, db)

def delete_team(team_id: int, db: Session) -> team_models.Team:
    team = get_team(team_id, db)
    return repository.delete_team(team, db)
    

# Helper: Check uniqueness by team name
def ensure_team_name_is_unique(team_name: str, db: Session) -> None:
    team = repository.get_team_by_name(team_name, db)
    if team:
        logger.warning(f"Duplicate team name: '{team_name}' already exists.")
        raise TeamNameExistsException(team_name)