from pydantic import BaseModel


class TeamCreateRequest(BaseModel):
    team_name: str

class TeamUpdateRequest(BaseModel):
    team_name: str

class TeamResponse(BaseModel):
    team_id: int
    team_name: str

    class Config:
        from_attributes = True