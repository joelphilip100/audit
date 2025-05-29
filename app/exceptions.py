from fastapi import HTTPException
from starlette import status

class EmployeeNotFoundException(HTTPException):
    def __init__(self, gpn: str = None):
        message = "Employee not found" if gpn is None else f"Employee with GPN {gpn} not found"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)

class EmployeeGpnExistsException(HTTPException):
    def __init__(self, gpn: str = None):
        message = "GPN already exists" if gpn is None else f"GPN {gpn} already exists"
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

class TeamNotFoundException(HTTPException):
    def __init__(self, team_id: int = None):
        message = "Team not found" if team_id is None else f"Team with ID {team_id} not found"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)

class TeamNameExistsException(HTTPException):
    def __init__(self, team_name: str = None):
        message = "Team name already exists" if team_name is None else f"Team {team_name} already exists"
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)