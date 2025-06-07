from typing import Type

from sqlalchemy.orm import Session
from app.employees import models as employee_models, schemas as employee_schema
from app.employees.repository import employee_repo
from app.employees.models import Employee
from app.loggers import logger
from app.exceptions import EmployeeNotFoundException
from app.employees import employee_util


def create_employee(employee_request: employee_schema.EmployeeCreateRequest, db: Session) -> employee_models.Employee:
    employee_util.ensure_gpn_is_unique(employee_request.gpn, db)
    new_employee = employee_models.Employee(
        gpn=employee_request.gpn,
        employee_name=employee_request.employee_name,
        team_id=employee_request.team_id
    )
    return employee_repo.create(new_employee, db)


def get_all_employees(db: Session) -> list[Type[Employee]]:
    return employee_repo.get_all(db)


def update_employee(gpn: str, updated_data: employee_schema.EmployeeUpdateRequest,
                    db: Session) -> employee_models.Employee:
    employee = get_employee_by_gpn(gpn, db)
    if updated_data.gpn != employee.gpn:
        logger.info(f"GPN for employee {gpn} changing from {employee.gpn} to {updated_data.gpn}")
        employee_util.ensure_gpn_is_unique(updated_data.gpn, db)
    employee.gpn = updated_data.gpn
    employee.employee_name = updated_data.employee_name
    employee.team_id = updated_data.team_id
    return employee_repo.update(employee, db)


def delete_employee(gpn: str, db: Session) -> None:
    employee = get_employee_by_gpn(gpn, db)
    employee_repo.delete(employee, db)


def get_employee_by_gpn(gpn: str, db: Session) -> employee_models.Employee:
    employee = employee_repo.get_by_field("gpn", gpn, db)
    if not employee:
        logger.warning(f"Employee with GPN {gpn} not found")
        raise EmployeeNotFoundException(gpn)
    return employee
