from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.models import team as team_models
from app.schemas import team as team_schema
from starlette import status

router = APIRouter(
    prefix="/teams",
    tags = ["teams"]
)

# Create team
@router.post("/", response_model=team_schema.TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(team_create_request: team_schema.TeamCreateRequest, db: Session = Depends(get_db)):
    existing_team = db.query(team_models.Team).filter(team_models.Team.team_name == team_create_request.team_name).first() 
    if existing_team:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Team with this name already exists")
    new_team = team_models.Team(team_name=team_create_request.team_name)
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    return new_team

# Get all teams
@router.get("/", response_model=list[team_schema.TeamResponse])
async def get_teams(db: Session = Depends(get_db)):
    return db.query(team_models.Team).all()


# Get team by ID
@router.get("/{team_id}", response_model=team_schema.TeamResponse)
async def get_team(team_id: int, db: Session = Depends(get_db)):
    team = get_team(team_id, db)
    return team

# Update team
@router.put("/{team_id}", response_model=team_schema.TeamResponse)
async def update_team(team_id: int, team_update_request: team_schema.TeamUpdateRequest, db: Session = Depends(get_db)):
    team = get_team(team_id, db)
    team.team_name = team_update_request.team_name
    db.commit()
    db.refresh(team)
    return team

# delete team
@router.delete("/{team_id}")
async def delete_team(team_id: int, db: Session = Depends(get_db)):
    team = get_team(team_id, db)
    db.delete(team)
    db.commit()
    return {"message": "Team deleted successfully"}

def get_team(team_id: int, db):
    team = db.query(team_models.Team).filter(team_models.Team.team_id == team_id).first()
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return team
