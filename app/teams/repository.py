from app.teams import models as team_models
from app.teams.schemas import TeamBase, TeamCreateRequest, TeamUpdateRequest
from app.core.base_repository import BaseRepository

from sqlalchemy.orm import Session


class TeamRepository(BaseRepository[TeamBase, TeamCreateRequest, TeamUpdateRequest]):
    def get_team_by_name(self, team_name: str, db: Session) -> team_models.Team | None:
        return db.query(team_models.Team).filter(team_models.Team.team_name == team_name).first()


team_repo = TeamRepository(team_models.Team, "team_id")
