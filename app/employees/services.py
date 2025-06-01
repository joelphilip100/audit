from typing import Type

from sqlalchemy.orm import Session
from app.employees import models as employee_models, schemas as employee_schema, repository
from app.employees.models import Employee
from app.teams import repository as team_repository
from app.loggers import logger
from app.exceptions import EmployeeGpnExistsException, TeamNotFoundException, EmployeeNotFoundException


def create_employee(employee_request: employee_schema.EmployeeCreateRequest, db: Session) -> employee_models.Employee:
    ensure_gpn_is_unique(employee_request.gpn, db)
    if employee_request.team_name:
        team_id = get_team_id(employee_request.team_name, db)
    else:
        team_id = None
    new_employee = employee_models.Employee(
        gpn=employee_request.gpn,
        employee_name=employee_request.employee_name,
        team_id=team_id
    )
    return repository.create_employee(new_employee, db)


def get_all_employees(db: Session) -> list[Type[Employee]]:
    return repository.get_all_employees(db)


def update_employee(gpn: str, updated_data: employee_schema.EmployeeUpdateRequest,
                    db: Session) -> employee_models.Employee:
    employee = get_employee_by_gpn(gpn, db)
    if updated_data.team_name:
        team_id = get_team_id(updated_data.team_name, db)
    else:
        team_id = None
    if updated_data.gpn != employee.gpn:
        logger.info(f"GPN for employee {gpn} changing from {employee.gpn} to {updated_data.gpn}")
        ensure_gpn_is_unique(updated_data.gpn, db)
    employee.gpn = updated_data.gpn
    employee.employee_name = updated_data.employee_name
    employee.team_id = team_id
    return repository.update_employee(employee, db)


def delete_employee(gpn: str, db: Session) -> None:
    employee = get_employee_by_gpn(gpn, db)
    repository.delete_employee(employee, db)


def get_employee_by_gpn(gpn: str, db: Session) -> employee_models.Employee:
    employee = repository.get_employee_by_gpn(gpn, db)
    if not employee:
        logger.warning(f"Employee with GPN {gpn} not found")
        raise EmployeeNotFoundException(gpn)
    return employee


# Helper: Check uniqueness by GPN
def ensure_gpn_is_unique(gpn: str, db: Session) -> None:
    employee = repository.get_employee_by_gpn(gpn, db)
    if employee:
        logger.warning(f"Employee creation/update failed: GPN {gpn} already exists.")
        raise EmployeeGpnExistsException(gpn)


# Helper: Validate team name
def get_team_id(team_name: str, db: Session) -> int:
    team = team_repository.get_team_by_name(team_name, db)
    if not team:
        logger.warning(f"Employee creation/update failed: Team {team_name} does not exist.")
        raise TeamNotFoundException()
    return team.team_id
