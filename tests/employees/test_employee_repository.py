import pytest

from app.employees.repository import employee_repo
from app.employees import models as employee_models
from sqlalchemy.exc import IntegrityError, InvalidRequestError

from tests.employees import employee_helper


@pytest.mark.real_db
def test_get_all_employees_empty(test_db):
    employees = employee_repo.get_all(test_db)
    assert len(employees) == 0


@pytest.mark.real_db
def test_create_employee(test_db):
    team = employee_helper.create_test_team("test_team", test_db)
    employee = employee_models.Employee(
        gpn="GPN100",
        employee_name="Alice Smith",
        team_id=team.team_id
    )

    created_employee = employee_repo.create(employee, test_db)

    assert created_employee.gpn == "GPN100"
    assert created_employee.employee_name == "Alice Smith"
    assert created_employee.team_id == team.team_id
    assert created_employee.team_name == team.team_name

@pytest.mark.real_db
def test_create_employee_without_team_id(test_db):
    employee = employee_models.Employee(
        gpn="GPN777",
        employee_name="Bob Johnson",
    )

    employee = employee_repo.create(employee, test_db)

    assert employee.gpn == "GPN777"
    assert employee.employee_name == "Bob Johnson"
    assert employee.team_id is None
    assert employee.team_name is None


@pytest.mark.real_db
def test_create_employee_with_invalid_team_id_type(test_db):
    employee = employee_models.Employee(
        gpn="GPN888",
        employee_name="Bob Johnson",
        team_id="invalid"
    )

    with pytest.raises(IntegrityError) as exc_info:
        employee_repo.create(employee, test_db)

    assert "FOREIGN KEY constraint failed" in str(exc_info.value)


@pytest.mark.real_db
def test_create_employee_when_team_does_not_exist(test_db):
    employee = employee_models.Employee(
        gpn="GPN101",
        employee_name="Bob Johnson",
        team_id=10000
    )

    with pytest.raises(IntegrityError) as exc_info:
        employee_repo.create(employee, test_db)

    assert "FOREIGN KEY constraint failed" in str(exc_info.value)


@pytest.mark.real_db
def test_create_employee_when_duplicate_gpn(test_db):
    details = employee_helper.create_test_employee("GPN101", "Daniel Smith", "team_1", test_db)

    employee = employee_models.Employee(
        gpn="GPN101",
        employee_name="Alice Smith",
        team_id=details[1].team_id
    )

    with pytest.raises(IntegrityError) as exc_info:
        employee_repo.create(employee, test_db)

    assert "UNIQUE constraint failed: employees.gpn" in str(exc_info.value)


@pytest.mark.real_db
def test_create_employee_when_employee_name_missing(test_db):
    team = employee_helper.create_test_team("test_employee_missing", test_db)
    employee = employee_models.Employee(
        gpn="GPN102",
        team_id=team.team_id
    )

    with pytest.raises(IntegrityError) as exc_info:
        employee_repo.create(employee, test_db)
    assert "NOT NULL constraint failed: employees.employee_name" in str(exc_info.value)


@pytest.mark.real_db
def test_create_employee_when_employee_gpn_missing(test_db):
    team = employee_helper.create_test_team("test_gpn_missing", test_db)
    employee = employee_models.Employee(
        employee_name="Alice Smith",
        team_id=team.team_id
    )

    with pytest.raises(IntegrityError) as exc_info:
        employee_repo.create(employee, test_db)

    assert "NOT NULL constraint failed: employees.gpn" in str(exc_info.value)


@pytest.mark.real_db
def test_get_all_employees(test_db):
    details = employee_helper.create_test_employee("GPN102", "Joel Philip", "team_2", test_db)
    team = details[1]

    employees = employee_repo.get_all(test_db)

    assert len(employees) > 0
    assert any(employee.gpn == "GPN102" for employee in employees)
    assert any(employee.employee_name == "Joel Philip" for employee in employees)
    assert any(employee.team_id == team.team_id for employee in employees)


@pytest.mark.real_db
def test_get_employee_by_gpn(test_db):
    details = employee_helper.create_test_employee("GPN103", "Garry David", "team_3", test_db)
    team = details[1]

    employee = employee_repo.get_by_field("gpn", "GPN103", test_db)

    assert employee.gpn == "GPN103"
    assert employee.employee_name == "Garry David"
    assert employee.team_id == team.team_id


@pytest.mark.real_db
def test_get_employee_by_gpn_invalid(test_db):
    employee = employee_repo.get_by_field("gpn", "InvalidGPN", test_db)

    assert employee is None


@pytest.mark.real_db
def test_update_employee(test_db):
    details = employee_helper.create_test_employee("GPN104", "John Doe", "team_4", test_db)
    employee = details[0]
    team = details[1]

    employee.employee_name = "Jennifer Doe"

    updated_employee = employee_repo.update(employee, test_db)

    assert updated_employee.gpn == "GPN104"
    assert updated_employee.employee_name == "Jennifer Doe"
    assert updated_employee.team_id == team.team_id


@pytest.mark.real_db
def test_update_employee_without_changes(test_db):
    details = employee_helper.create_test_employee("GPN105", "Thomas Valentine", "team_5", test_db)
    employee = details[0]
    team = details[1]

    updated_employee = employee_repo.update(employee, test_db)

    assert updated_employee.gpn == "GPN105"
    assert updated_employee.employee_name == "Thomas Valentine"
    assert updated_employee.team_id == team.team_id
    assert updated_employee.team_name == "TEAM_5"


@pytest.mark.real_db
def test_update_employee_with_existing_gpn(test_db):
    employee_helper.create_test_employee("GPN106", "Christy James", "team_6", test_db)
    employee2_details = employee_helper.create_test_employee("GPN107", "Albert Smith", "team_7", test_db)
    employee2 = employee2_details[0]

    employee2.gpn = "GPN106"

    with pytest.raises(IntegrityError) as exc_info:
        employee_repo.update(employee2, test_db)

    assert "UNIQUE constraint failed: employees.gpn" in str(exc_info.value)


@pytest.mark.real_db
def test_delete_employee(test_db):
    details = employee_helper.create_test_employee("GPN108", "John Williams", "team_8", test_db)
    employee = details[0]

    employee_repo.delete(employee, test_db)
    deleted_employee = employee_repo.get_by_field("gpn", "GPN108", test_db)

    assert deleted_employee is None


@pytest.mark.real_db
def test_delete_employee_not_found(test_db):
    with pytest.raises(InvalidRequestError):
        employee_repo.delete(employee_models.Employee(gpn="GPN109", employee_name="John Doe"), test_db)
