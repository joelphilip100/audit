from sqlalchemy.orm import Session
from app.teams import models as team_models

def create_team(team: team_models.Team, db: Session) -> team_models.Team:
    db.add(team)
    db.commit()
    db.refresh(team)
    return team

def get_all_teams(db: Session) -> list[team_models.Team]:
    return db.query(team_models.Team).all()

def get_team_by_id(team_id: int, db: Session) -> team_models.Team:
    return db.query(team_models.Team).filter(team_models.Team.team_id == team_id).first()

def update_team_name(team: team_models.Team, db: Session) -> team_models.Team:
    db.commit()
    db.refresh(team)
    return team

def delete_team(team: team_models.Team, db: Session) -> None:
    db.delete(team)
    db.commit()

def get_team_by_name(team_name: str, db: Session) -> team_models.Team:
    return db.query(team_models.Team).filter(team_models.Team.team_name == team_name).first()