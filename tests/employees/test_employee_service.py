import pytest
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.employees import services as employee_services
from app.employees import schemas as employee_schema
from app.exceptions import EmployeeGpnExistsException, TeamNotFoundException, EmployeeNotFoundException

from tests.employees import employee_helper

SCHEMAS = [employee_schema.EmployeeCreateRequest, employee_schema.EmployeeUpdateRequest]


def test_get_all_employees_empty(test_db):
    employees = employee_services.get_all_employees(test_db)
    assert len(employees) == 0


def test_create_employee(test_db):
    team = employee_helper.create_test_team("team_ces1", test_db)
    employee_request = employee_schema.EmployeeCreateRequest(
        gpn="GPN_CES1",
        employee_name="Alice Smith",
        team_id=team.team_id
    )

    new_employee = employee_services.create_employee(employee_request, test_db)

    assert new_employee.gpn == "GPN_CES1"
    assert new_employee.employee_name == "Alice Smith"
    assert new_employee.team_id == team.team_id
    assert new_employee.team_name == team.team_name


def test_create_employee_without_team_name(test_db):
    employee_request = employee_schema.EmployeeCreateRequest(
        gpn="GPN_CES2",
        employee_name="Alice Smith"
    )

    new_employee = employee_services.create_employee(employee_request, test_db)

    assert new_employee.gpn == "GPN_CES2"
    assert new_employee.employee_name == "Alice Smith"
    assert new_employee.team_id is None


def test_create_employee_with_duplicate_gpn(test_db):
    gpn = "GPN_CES3"
    employee, team = employee_helper.create_test_employee(gpn, "Alice Smith", "team_ces3", test_db)
    employee_request = employee_schema.EmployeeCreateRequest(
        gpn="GPN_CES3",
        employee_name="Alice Smith",
        team_id=team.team_id
    )

    with pytest.raises(EmployeeGpnExistsException) as exc_info:
        employee_services.create_employee(employee_request, test_db)

    assert f"GPN {gpn} already exists" in str(exc_info.value)


def test_create_employee_with_invalid_team_id(test_db):
    employee_request = employee_schema.EmployeeCreateRequest(
        gpn="GPN_CES4",
        employee_name="Alice Smith",
        team_id=100000
    )

    with pytest.raises(IntegrityError) as exc_info:
        employee_services.create_employee(employee_request, test_db)

    assert "FOREIGN KEY constraint failed" in str(exc_info.value)


def test_get_all_employees(test_db):
    employee_helper.create_test_employee("GPN_RES1", "Alice Smith", "TEAM_RES1", test_db)
    employee_helper.create_test_employee("GPN_RES2", "Bob Johnson", "TEAM_RES2", test_db)
    employee_helper.create_test_employee("GPN_RES3", "Charlie Brown", "TEAM_RES3", test_db)

    employees = employee_services.get_all_employees(test_db)

    assert any(employee.gpn == "GPN_RES1" for employee in employees)
    assert any(employee.gpn == "GPN_RES2" for employee in employees)
    assert any(employee.gpn == "GPN_RES3" for employee in employees)


def test_get_employee_by_gpn(test_db):
    created_employee, team = employee_helper.create_test_employee("GPN_RES4", "Alice Smith", "TEAM_RES4", test_db)

    employee = employee_services.get_employee_by_gpn("GPN_RES4", test_db)

    assert employee.gpn == "GPN_RES4"
    assert employee.employee_name == "Alice Smith"
    assert employee.team_id == team.team_id
    assert employee.team_name == team.team_name


def test_get_employee_by_gpn_not_found(test_db):
    gpn = "GPN_RES5"

    with pytest.raises(EmployeeNotFoundException) as exc_info:
        employee_services.get_employee_by_gpn(gpn, test_db)

    assert f"Employee with GPN {gpn} not found" in str(exc_info.value)


def test_update_employee(test_db):
    gpn = "GPN_UES1"
    created_employee, team = employee_helper.create_test_employee(gpn, "Alice Smith", "TEAM_UES1", test_db)
    employee_request = employee_schema.EmployeeUpdateRequest(
        gpn=gpn,
        employee_name="John Smith",
        team_id=team.team_id
    )

    updated_employee = employee_services.update_employee(gpn, employee_request, test_db)

    assert updated_employee.gpn == gpn
    assert updated_employee.employee_name == "John Smith"
    assert updated_employee.team_id == team.team_id


def test_update_employee_no_changes(test_db):
    gpn = "GPN_UES2"
    created_employee, team = employee_helper.create_test_employee(gpn, "Alice Smith", "TEAM_UES2", test_db)
    employee_request = employee_schema.EmployeeUpdateRequest(
        gpn=gpn,
        employee_name="Alice Smith",
        team_id=team.team_id
    )

    updated_employee = employee_services.update_employee(gpn, employee_request, test_db)

    assert updated_employee.gpn == gpn
    assert updated_employee.employee_name == "Alice Smith"
    assert updated_employee.team_id == team.team_id


def test_update_employee_with_gpn_not_found(test_db):
    invalid_gpn = "10000"
    team = employee_helper.create_test_team("TEAM_UES3", test_db)

    employee_request = employee_schema.EmployeeUpdateRequest(
        gpn=invalid_gpn,
        employee_name="Alice Smith",
        team_id=team.team_id
    )

    with pytest.raises(EmployeeNotFoundException) as exc_info:
        employee_services.update_employee(invalid_gpn, employee_request, test_db)

    assert f"Employee with GPN {invalid_gpn} not found" in str(exc_info.value)


def test_update_employee_with_different_gpn_valid(test_db):
    gpn = "GPN_UES4"
    created_employee, team = employee_helper.create_test_employee(gpn, "Alice Smith", "TEAM_UES4", test_db)
    employee_request = employee_schema.EmployeeUpdateRequest(
        gpn="GPN_UES4_NEW",
        employee_name="Alice Smith",
        team_id=team.team_id
    )

    updated_employee = employee_services.update_employee(gpn, employee_request, test_db)

    assert updated_employee.gpn == "GPN_UES4_NEW"
    assert updated_employee.employee_name == "Alice Smith"
    assert updated_employee.team_id == team.team_id


def test_update_employee_with_existing_gpn(test_db):
    employee1, team1 = employee_helper.create_test_employee("GPN_UES5", "Alice Smith", "TEAM_UES5", test_db)
    employee2, team2 = employee_helper.create_test_employee("GPN_UES6", "George Smith", "TEAM_UES6", test_db)

    new_gpn_to_update = employee1.gpn
    # Update employee2 with employee1 gpn
    employee_request = employee_schema.EmployeeUpdateRequest(
        gpn=new_gpn_to_update,
        employee_name="George Smith",
        team_id=team2.team_id
    )

    with pytest.raises(EmployeeGpnExistsException) as exc_info:
        employee_services.update_employee(employee2.gpn, employee_request, test_db)

    assert f"GPN {new_gpn_to_update} already exists" in str(exc_info.value)


def test_update_employee_with_invalid_team_name(test_db):
    gpn = "GPN_UES7"
    employee_helper.create_test_employee(gpn, "Alice Smith", "TEAM_UES7", test_db)
    employee_request = employee_schema.EmployeeUpdateRequest(
        gpn=gpn,
        employee_name="Alice Smith",
        team_id=100000
    )

    with pytest.raises(IntegrityError) as exc_info:
        employee_services.update_employee(gpn, employee_request, test_db)

    assert "FOREIGN KEY constraint failed" in str(exc_info.value)


def test_update_employee_with_team_name_none(test_db):
    gpn = "GPN_UES8"
    employee_helper.create_test_employee(gpn, "Alice Smith", "TEAM_UES8", test_db)
    employee_request = employee_schema.EmployeeUpdateRequest(
        gpn=gpn,
        employee_name="Alice Smith"
    )

    updated_employee = employee_services.update_employee(gpn, employee_request, test_db)

    assert updated_employee.gpn == gpn
    assert updated_employee.employee_name == "Alice Smith"
    assert updated_employee.team_id is None


def test_delete_employee(test_db):
    gpn = "GPN_DES1"
    employee_helper.create_test_employee(gpn, "Alice Smith", "TEAM_DES1", test_db)

    employee_services.delete_employee(gpn, test_db)

    employees = employee_services.get_all_employees(test_db)
    assert not any(employee.gpn == gpn for employee in employees)


def test_delete_employee_not_found(test_db):
    gpn = "GPN_DES2"

    with pytest.raises(EmployeeNotFoundException) as exc_info:
        employee_services.delete_employee(gpn, test_db)

    assert f"Employee with GPN {gpn} not found" in str(exc_info.value)


def test_recreate_employee_after_deletion(test_db):
    gpn = "GPN_DES3"
    team_name = "TEAM_DES3"
    team = employee_helper.create_test_team(team_name, test_db)
    employee_services.create_employee(
        employee_schema.EmployeeCreateRequest(gpn=gpn, employee_name="Alice Smith", team_id=team.team_id), test_db)
    employee_services.delete_employee(gpn, test_db)
    employee_services.create_employee(
        employee_schema.EmployeeCreateRequest(gpn=gpn, employee_name="Alice Smith", team_id=team.team_id), test_db)

    employee = employee_services.get_employee_by_gpn(gpn, test_db)

    assert employee.gpn == gpn


# Schema tests
@pytest.mark.parametrize("schemas", SCHEMAS)
def test_gpn_is_converted_to_uppercase(schemas):
    request = schemas(
        gpn="gpn123",
        employee_name="Alice Smith",
        team_id=1
    )

    assert request.gpn == "GPN123"


@pytest.mark.parametrize("schemas", SCHEMAS)
def test_employee_name_title_case_conversion(schemas):
    request = schemas(
        gpn="gpn123",
        employee_name="alice smith",
        team_name="team_one"
    )

    assert request.employee_name == "Alice Smith"


@pytest.mark.parametrize(
    "field_name, data, expected_message",
    [
        ("employee_name", {"gpn": "GPN_MISS", "team_id": 1},
         "1 validation error for EmployeeCreateRequest\nemployee_name"),
        ("gpn", {"employee_name": "Alice", "team_id": 1},
         "1 validation error for EmployeeCreateRequest\ngpn")
    ]
)
def test_create_request_without_fields(field_name, data, expected_message):
    with pytest.raises(ValidationError) as exc_info:
        employee_schema.EmployeeCreateRequest(
            **data,
        )

    assert expected_message in str(exc_info.value)


@pytest.mark.parametrize(
    "field_name, data, expected_message",
    [
        ("employee_name", {"gpn": "GPN_MISS", "team_id": 1},
         "1 validation error for EmployeeUpdateRequest\nemployee_name"),
        ("gpn", {"employee_name": "Alice", "team_id": 1},
         "1 validation error for EmployeeUpdateRequest\ngpn")
    ]
)
def test_create_request_without_fields(field_name, data, expected_message):
    with pytest.raises(ValidationError) as exc_info:
        employee_schema.EmployeeUpdateRequest(
            **data,
        )

    assert expected_message in str(exc_info.value)


@pytest.mark.parametrize("schemas", SCHEMAS)
@pytest.mark.parametrize(
    "field_name, data, expected_message",
    [
        ("gpn", {"gpn": "a", "employee_name": "Alice"}, "String should have at least 2 characters"),
        ("gpn", {"gpn": "a" * 16, "employee_name": "Alice"}, "String should have at most 15 characters"),
        ("employee_name", {"gpn": "GPN1", "employee_name": "A"}, "String should have at least 2 characters"),
        ("employee_name", {"gpn": "GPN2", "employee_name": "A" * 51}, "String should have at most 50 characters"),
    ]
)
def test_create_update_request_field_length_validation(schemas, field_name, data, expected_message):
    with pytest.raises(ValidationError) as exc_info:
        schemas(**data)

    assert expected_message in str(exc_info.value)


@pytest.mark.parametrize("schemas", SCHEMAS)
@pytest.mark.parametrize(
    "gpn_input, employee_name_input, expected_gpn, expected_name",
    [
        ("  GPN123  ", " Alice ", "GPN123", "Alice"),
        ("\tGPN999", "Bob\t", "GPN999", "Bob"),
        ("GPN1", "Alice Smith", "GPN1", "Alice Smith"),
    ]
)
def test_create_update_request_strip_whitespace_on_fields(schemas, gpn_input, employee_name_input,
                                                          expected_gpn, expected_name):
    employee = schemas(
        gpn=gpn_input,
        employee_name=employee_name_input,
        team_id=1
    )

    assert employee.gpn == expected_gpn
    assert employee.employee_name == expected_name
    assert employee.team_id == 1
