import pytest

from unittest.mock import patch
from app.employees.employee_util import ensure_gpn_is_unique
from app.exceptions import EmployeeGpnExistsException
from app.employees.models import Employee


@pytest.mark.fake_db
def test_gpn_is_unique(fake_db):
    # Simulate no employee found
    with patch("app.employees.repository.employee_repo.get_by_field", return_value=None):
        # Should not raise
        ensure_gpn_is_unique("GPN999", fake_db)


@pytest.mark.fake_db
def test_gpn_is_not_unique(fake_db):
    # Simulate employee found
    with patch("app.employees.repository.employee_repo.get_by_field", return_value=Employee(gpn="GPN999")):
        with pytest.raises(EmployeeGpnExistsException):
            ensure_gpn_is_unique("GPN999", fake_db)