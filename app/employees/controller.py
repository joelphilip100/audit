from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.employees import schemas as employee_schema, services
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
    new_employee = services.create_employee(employee_request, db)
    logger.info(f"Employee created with GPN: {new_employee.gpn}")
    return new_employee

# Get all employees
@router.get("/", response_model=list[employee_schema.EmployeeResponse])
async def get_all_employees(db: Session = Depends(get_db)):
    logger.info("Fetching all employees")
    return services.get_all_employees(db)

# Get employee by GPN
@router.get("/{gpn}", response_model=employee_schema.EmployeeResponse)
async def get_employee(gpn: str, db: Session = Depends(get_db)):
    logger.info(f"Fetching employee with GPN: {gpn}")
    return services.get_employee_by_gpn(gpn, db)

# Update employee
@router.put("/{gpn}", response_model=employee_schema.EmployeeResponse)
async def update_employee(gpn: str, updated_data: employee_schema.EmployeeUpdateRequest, db: Session = Depends(get_db)):
    logger.info(f"Updating employee with GPN: {gpn}")
    employee = services.update_employee(gpn, updated_data, db)
    logger.info(f"Employee with GPN {gpn} updated successfully")
    return employee

# Delete employee
@router.delete("/{gpn}")
async def delete_employee(gpn: str, db: Session = Depends(get_db)):
    logger.info(f"Deleting employee with GPN: {gpn}")
    services.delete_employee(gpn, db)
    logger.info(f"Employee with GPN {gpn} deleted successfully")
    return {"message": "Employee deleted successfully"}