from sqlalchemy.orm import Session
from app.employees import repository
from app.loggers import logger
from app.exceptions import EmployeeGpnExistsException


def ensure_gpn_is_unique(gpn: str, db: Session) -> None:
    employee = repository.get_employee_by_gpn(gpn, db)
    if employee:
        logger.warning(f"Employee creation/update failed: GPN {gpn} already exists.")
        raise EmployeeGpnExistsException(gpn)
