from pydantic import BaseModel, Field, field_validator


class TeamBase(BaseModel):
    team_name: str = Field(..., min_length=2, max_length=20)

    #  noinspection PyNestedDecorators
    @field_validator("team_name")
    @classmethod
    def team_name_is_uppercase(cls, value: str) -> str:
        return value.upper() if value else value


class TeamCreateRequest(TeamBase):
    pass


class TeamUpdateRequest(TeamBase):
    pass


class TeamResponse(BaseModel):
    team_id: int
    team_name: str

    class Config:
        from_attributes = True
