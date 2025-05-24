from pydantic import BaseModel

class EmployeeCreateRequest(BaseModel):
    gpn: str
    employee_name: str
    team_name: str

class EmployeeUpdateRequest(BaseModel):
    gpn: str
    employee_name: str
    team_name: str


class EmployeeResponse(BaseModel):
    employee_id: int
    gpn: str
    employee_name: str
    team_name: str

    class Config:
        from_attributes = True