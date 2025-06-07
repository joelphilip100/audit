
from sqlalchemy.orm import Session

from app.teams import repository
from app.loggers import logger
from app.exceptions import TeamNameExistsException


def ensure_team_name_is_unique(team_name: str, db: Session) -> None:
    team = repository.get_team_by_name(team_name, db)
    if team:
        logger.warning(f"Duplicate team name: '{team_name}' already exists.")
        raise TeamNameExistsException(team_name)