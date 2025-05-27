from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import employee as employee_schema
from app.dependencies import get_db
from app.models import employee as employee_models
from app.models import team as team_models
from app.constants import EMPLOYEE_GPN_EXISTS, EMPLOYEE_NOT_FOUND, TEAM_NOT_FOUND
from app.loggers import logger
from starlette import status

router = APIRouter(
    prefix="/employees",
    tags = ["employees"]
)

# Create employee
@router.post("/", response_model=employee_schema.EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(employee_request: employee_schema.EmployeeCreateRequest, db: Session = Depends(get_db)):
    logger.info(f"Creating employee with GPN: {employee_request.gpn}")

    # Ensure GPN is unique
    ensure_gpn_is_unique(employee_request.gpn, db)

    # Get team_id or raise exception if not found
    team_id = get_team_id(employee_request.team_name, db)

    # Create and persist new employee
    new_employee = employee_models.Employee(
        gpn=employee_request.gpn,
        employee_name=employee_request.employee_name,
        team_id=team_id
    )
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    logger.info(f"Employee created with GPN: {new_employee.gpn}")
    return new_employee

# Get all employees
@router.get("/", response_model=list[employee_schema.EmployeeResponse])
async def get_all_employees(db: Session = Depends(get_db)):
    logger.info("Fetching all employees")
    return db.query(employee_models.Employee).all()

# Get employee by GPN
@router.get("/{gpn}", response_model=employee_schema.EmployeeResponse)
async def get_employee(gpn: str, db: Session = Depends(get_db)):
    logger.info(f"Fetching employee with GPN: {gpn}")
    employee = get_employee_by_gpn(gpn, db)
    return employee

# Update employee
@router.put("/{gpn}", response_model=employee_schema.EmployeeResponse)
async def update_employee(gpn: str, updated_data: employee_schema.EmployeeUpdateRequest, db: Session = Depends(get_db)):
    logger.info(f"Updating employee with GPN: {gpn}")
    employee = get_employee_by_gpn(gpn, db)
    if updated_data.gpn != employee.gpn:
        logger.info(f"GPN for employee {gpn} changing from {employee.gpn} to {updated_data.gpn}")
        ensure_gpn_is_unique(updated_data.gpn, db)
    employee.gpn = updated_data.gpn
    employee.employee_name = updated_data.employee_name
    employee.team_id = get_team_id(updated_data.team_name, db)
    db.commit()
    db.refresh(employee)
    logger.info(f"Employee with GPN {gpn} updated successfully")
    return employee

# Delete employee
@router.delete("/{gpn}")
async def delete_employee(gpn: str, db: Session = Depends(get_db)):
    logger.info(f"Deleting employee with GPN: {gpn}")
    employee = get_employee_by_gpn(gpn, db)
    db.delete(employee)
    db.commit()
    logger.info(f"Employee with GPN {gpn} deleted successfully")
    return {"message": "Employee deleted successfully"}

# Helper: Get employee or raise 404
def get_employee_by_gpn(gpn: str, db: Session) -> employee_models.Employee:
    employee = db.query(employee_models.Employee).filter(employee_models.Employee.gpn == gpn).first()
    if not employee:
        logger.warning(f"Employee with GPN {gpn} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=EMPLOYEE_NOT_FOUND)
    return employee

# Helper: Check uniqueness by GPN
def ensure_gpn_is_unique(gpn: str, db: Session) -> None:
    employee = db.query(employee_models.Employee).filter(employee_models.Employee.gpn == gpn).first()
    if employee:
        logger.warning(f"Employee creation/update failed: GPN {gpn} already exists.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=EMPLOYEE_GPN_EXISTS)
    
# Helper: Validate team name
def get_team_id(team_name: str, db: Session) -> int:
    team = db.query(team_models.Team).filter(team_models.Team.team_name == team_name).first()
    if not team:
        logger.warning(f"Employee creation/update failed: Team {team_name} does not exist.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=TEAM_NOT_FOUND)
    return team.team_id
