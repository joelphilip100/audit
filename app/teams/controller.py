from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.teams import schemas as team_schema, services
from app.constants import TEAM_DELETED
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
    new_team = services.create_team(team_create_request.team_name, db)
    logger.info(f"Team {new_team.team_name} created successfully with ID: {new_team.team_id}")
    return new_team

# Get all teams
@router.get("/", response_model=list[team_schema.TeamResponse])
async def get_teams(db: Session = Depends(get_db)):
    logger.info("Fetching all teams")
    return services.get_all_teams(db)


# Get team by ID
@router.get("/{team_id}", response_model=team_schema.TeamResponse)
async def get_team(team_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching team with ID: {team_id}")
    return services.get_team(team_id, db)

# Update team
@router.put("/{team_id}", response_model=team_schema.TeamResponse)
async def update_team(team_id: int, team_update_request: team_schema.TeamUpdateRequest, db: Session = Depends(get_db)):
    logger.info(f"Updating team with ID: {team_id}")
    team = services.update_team(team_id, team_update_request.team_name, db)
    logger.info(f"Team with ID: {team_id} updated successfully")
    return team

# delete team
@router.delete("/{team_id}")
async def delete_team(team_id: int, db: Session = Depends(get_db)):
    logger.info(f"Deleting team with ID: {team_id}")
    team = services.delete_team(team_id, db)
    logger.info(f"Team with ID: {team_id} deleted successfully")
    return {"message": TEAM_DELETED}

