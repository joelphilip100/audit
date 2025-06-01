from typing import Type

from sqlalchemy.orm import Session
from app.employees import models as employee_models
from app.employees.models import Employee


def create_employee(employee: employee_models.Employee, db: Session) -> employee_models.Employee:
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def get_all_employees(db: Session) -> list[Type[Employee]]:
    return db.query(employee_models.Employee).all()


def get_employee_by_gpn(gpn: str, db: Session) -> employee_models.Employee | None:
    return db.query(employee_models.Employee).filter(employee_models.Employee.gpn == gpn).first()


def update_employee(employee: employee_models.Employee, db: Session) -> employee_models.Employee:
    db.commit()
    db.refresh(employee)
    return employee


def delete_employee(employee: employee_models.Employee, db: Session) -> None:
    db.delete(employee)
    db.commit()
