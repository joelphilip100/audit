from app.employees import models as employee_models
from app.employees.schemas import EmployeeBase, EmployeeCreateRequest, EmployeeUpdateRequest
from app.core.base_repository import BaseRepository


class EmployeeRepository(BaseRepository[EmployeeBase, EmployeeCreateRequest, EmployeeUpdateRequest]):
    pass


employee_repo = EmployeeRepository(employee_models.Employee, "gpn")
