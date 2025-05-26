from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.models import team as team_models
from app.schemas import team as team_schema
from app.constants import TEAM_NAME_EXISTS, TEAM_NOT_FOUND, TEAM_DELETED 
from app.loggers import logger
from starlette import status

router = APIRouter(
    prefix="/teams",
    tags = ["teams"]
)

# Create team
@router.post("/", response_model=team_schema.TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(team_create_request: team_schema.TeamCreateRequest, db: Session = Depends(get_db)):
    logger.info(f"Creating team with name: {team_create_request.team_name}")
    ensure_team_name_is_unique(team_create_request.team_name, db)
    new_team = team_models.Team(team_name=team_create_request.team_name)
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    logger.info(f"Team {new_team.team_name} created successfully with ID: {new_team.team_id}")
    return new_team

# Get all teams
@router.get("/", response_model=list[team_schema.TeamResponse])
async def get_teams(db: Session = Depends(get_db)):
    logger.info("Fetching all teams")
    return db.query(team_models.Team).all()


# Get team by ID
@router.get("/{team_id}", response_model=team_schema.TeamResponse)
async def get_team(team_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching team with ID: {team_id}")
    team = get_team_or_404(team_id, db)
    return team

# Update team
@router.put("/{team_id}", response_model=team_schema.TeamResponse)
async def update_team(team_id: int, team_update_request: team_schema.TeamUpdateRequest, db: Session = Depends(get_db)):
    logger.info(f"Updating team with ID: {team_id}")
    team = get_team_or_404(team_id, db)
    ensure_team_name_is_unique(team_update_request.team_name, db)
    team.team_name = team_update_request.team_name
    db.commit()
    db.refresh(team)
    logger.info(f"Team with ID: {team_id} updated successfully")
    return team

# delete team
@router.delete("/{team_id}")
async def delete_team(team_id: int, db: Session = Depends(get_db)):
    logger.info(f"Deleting team with ID: {team_id}")
    team = get_team_or_404(team_id, db)
    db.delete(team)
    db.commit()
    logger.info(f"Team {team.team_name} with ID: {team_id} deleted successfully")
    return {"message": TEAM_DELETED}

# Helper: Get team or raise 404
def get_team_or_404(team_id: int, db) -> team_models.Team:
    team = db.query(team_models.Team).filter(team_models.Team.team_id == team_id).first()
    if not team:
        logger.warning(f"Team with ID {team_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=TEAM_NOT_FOUND)
    return team

# Helper: Check uniqueness by team name
def ensure_team_name_is_unique(team_name: str, db: Session) -> None:
    team = db.query(team_models.Team).filter(team_models.Team.team_name == team_name).first()
    if team:
        logger.warning(f"Duplicate team name: '{team_name}' already exists.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=TEAM_NAME_EXISTS)
