from sqlalchemy.orm import Session
from app.employees.repository import employee_repo
from app.loggers import logger
from app.exceptions import EmployeeGpnExistsException


def ensure_gpn_is_unique(gpn: str, db: Session) -> None:
    employee = employee_repo.get_by_field("gpn", gpn, db)
    if employee:
        logger.warning(f"Employee creation/update failed: GPN {gpn} already exists.")
        raise EmployeeGpnExistsException(gpn)
