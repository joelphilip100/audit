from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import employee as employee_schema
from app.dependencies import get_db
from app.models import employee as employee_models

router = APIRouter(
    prefix="/employees",
    tags = ["employees"]
)

# Create employee
@router.post("/", response_model=employee_schema.EmployeeResponse)
async def create_employee(employee: employee_schema.EmployeeCreateRequest, db: Session = Depends(get_db)):
    existing_employee = db.query(employee_models.Employee).filter(employee_models.Employee.gpn == employee.gpn).first()
    if existing_employee:
        raise HTTPException(status_code=400, detail="Employee with this GPN already exists")
    new_employee = employee_models.Employee(gpn=employee.gpn, employee_name=employee.employee_name, team_name=employee.team_name)
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee

# Get all employees
@router.get("/", response_model=list[employee_schema.EmployeeResponse])
async def get_employees(db: Session = Depends(get_db)):
    return db.query(employee_models.Employee).all()

# Get employee by GPN
@router.get("/{gpn}", response_model=employee_schema.EmployeeResponse)
async def get_employee(gpn: str, db: Session = Depends(get_db)):
    employee = db.query(employee_models.Employee).filter(employee_models.Employee.gpn == gpn).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.put("/{gpn}", response_model=employee_schema.EmployeeResponse)
async def update_employee(gpn: str, updated_employee: employee_schema.EmployeeUpdateRequest, db: Session = Depends(get_db)):
    employee = db.query(employee_models.Employee).filter(employee_models.Employee.gpn == gpn).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    employee.gpn = updated_employee.gpn
    employee.employee_name = updated_employee.employee_name
    employee.team_name = updated_employee.team_name
    db.commit()
    db.refresh(employee)
    return employee

@router.delete("/{gpn}")
async def delete_employee(gpn: str, db: Session = Depends(get_db)):
    employee = db.query(employee_models.Employee).filter(employee_models.Employee.gpn == gpn).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(employee)
    db.commit()
    return {"message": "Employee deleted successfully"}
    

