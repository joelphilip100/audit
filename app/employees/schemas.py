from pydantic import BaseModel

class EmployeeCreateRequest(BaseModel):
    gpn: str
    employee_name: str
    team_name: str | None

class EmployeeUpdateRequest(BaseModel):
    gpn: str
    employee_name: str
    team_name: str | None


class EmployeeResponse(BaseModel):
    employee_id: int
    gpn: str
    employee_name: str
    team_name: str | None

    class Config:
        from_attributes = True