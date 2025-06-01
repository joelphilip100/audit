def test_get_all_employees_returns_empty_list(client):
    response = client.get("/employees/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_all_employees_returns_list_of_employees(client):
    team_name = "TEAM_REC1"
    client.post("/teams/", json={"team_name": team_name})
    client.post("/employees/", json={"gpn": "GPN_REC1", "employee_name": "John Doe", "team_name": team_name})
    client.post("/employees/", json={"gpn": "GPN_REC2", "employee_name": "Davis Smith", "team_name": team_name})
    response = client.get("/employees/")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert any(employee["gpn"] == "GPN_REC1" for employee in response.json())
    assert any(employee["gpn"] == "GPN_REC2" for employee in response.json())
    assert any(employee["employee_name"] == "Davis Smith" for employee in response.json())
    assert any(employee["employee_name"] == "John Doe" for employee in response.json())
    assert any(employee["team_name"] == team_name for employee in response.json())
    assert any(employee["employee_id"] is not None for employee in response.json())


def test_get_employee_by_gpn_returns_employee(client):
    team_name = "TEAM_REC2"
    client.post("/teams/", json={"team_name": team_name})
    client.post("/employees/", json={"gpn": "GPN_REC3", "employee_name": "John Doe", "team_name": team_name})
    response = client.get("/employees/GPN_REC3")
    assert response.status_code == 200
    assert response.json()["employee_id"] is not None
    assert response.json()["gpn"] == "GPN_REC3"
    assert response.json()["employee_name"] == "John Doe"
    assert response.json()["team_name"] == team_name


def test_get_employee_invalid_gpn(client):
    response = client.get("/employees/GPN_INVALID")
    assert response.status_code == 404


def test_create_employee(client):
    team_name = "TEAM_CEC1"
    client.post("/teams/", json={"team_name": team_name})
    response = client.post("/employees/", json={"gpn": "GPN_CEC1", "employee_name": "John Doe", "team_name": team_name})
    assert response.status_code == 201
    assert response.json()["employee_id"] is not None
    assert response.json()["gpn"] == "GPN_CEC1"
    assert response.json()["employee_name"] == "John Doe"
    assert response.json()["team_name"] == team_name


def test_create_employee_when_gpn_already_exists(client):
    team_name = "TEAM_CEC2"
    client.post("/teams/", json={"team_name": team_name})
    client.post("/employees/", json={"gpn": "GPN_CEC2", "employee_name": "John Doe", "team_name": team_name})
    response = client.post("/employees/", json={"gpn": "GPN_CEC2", "employee_name": "Davis Smith", "team_name": team_name})
    assert response.status_code == 400


def test_create_employee_when_team_does_not_exist(client):
    response = client.post("/employees/", json={"gpn": "GPN_CEC3", "employee_name": "John Doe", "team_name": "non-existent-team"})
    assert response.status_code == 404


def test_create_employee_when_team_name_not_provided(client):
    response = client.post("/employees/", json={"gpn": "GPN_CEC4", "employee_name": "John Doe"})
    assert response.status_code == 201
    assert response.json()["team_name"] is None
    assert response.json()["employee_id"] is not None
    assert response.json()["gpn"] == "GPN_CEC4"
    assert response.json()["employee_name"] == "John Doe"


def test_create_employee_gpn_not_provided(client):
    response = client.post("/employees/", json={"team_name": "TEAM_CEC5", "employee_name": "John Doe"})
    assert response.status_code == 422


def test_create_employee_employee_name_not_provided(client):
    response = client.post("/employees/", json={"gpn": "GPN_CEC6", "team_name": "TEAM_CEC6"})
    assert response.status_code == 422


def test_update_employee(client):
    team_name = "TEAM_UEC1"
    client.post("/teams/", json={"team_name": team_name})
    client.post("/employees/", json={"gpn": "GPN_UEC1", "employee_name": "Alice Smith", "team_name": team_name})
    response = client.put("/employees/GPN_UEC1", json={"gpn": "GPN_UEC1", "employee_name": "John Doe", "team_name": team_name})
    assert response.status_code == 200
    assert response.json()["employee_id"] is not None
    assert response.json()["gpn"] == "GPN_UEC1"
    assert response.json()["employee_name"] == "John Doe"
    assert response.json()["team_name"] == team_name


def test_update_employee_invalid_gpn(client):
    response = client.put("/employees/GPN_INVALID", json={"gpn": "GPN_INVALID", "employee_name": "John Doe", "team_name": "team_invalid"})
    assert response.status_code == 404


def test_update_employee_when_team_does_not_exist(client):
    response = client.put("/employees/GPN_UEC2", json={"gpn": "GPN_UEC2", "employee_name": "John Doe", "team_name": "non-existent-team"})
    assert response.status_code == 404


def test_update_employee_when_team_name_not_provided(client):
    client.post("/employees/", json={"gpn": "GPN_UEC3", "employee_name": "Alice Smith"})
    response = client.put("/employees/GPN_UEC3", json={"gpn": "GPN_UEC3", "employee_name": "John Doe"})
    assert response.status_code == 200
    assert response.json()["employee_id"] is not None
    assert response.json()["gpn"] == "GPN_UEC3"
    assert response.json()["employee_name"] == "John Doe"
    assert response.json()["team_name"] is None


def test_update_employee_gpn_valid(client):
    team_name = "TEAM_UEC4"
    client.post("/teams/", json={"team_name": team_name})
    client.post("/employees/", json={"gpn": "GPN_UEC4", "employee_name": "Alice Smith", "team_name": team_name})
    response = client.put("/employees/GPN_UEC4", json={"gpn": "GPN_UEC5", "employee_name": "John Doe", "team_name": team_name})
    assert response.status_code == 200
    assert response.json()["employee_id"] is not None
    assert response.json()["gpn"] == "GPN_UEC5"
    assert response.json()["employee_name"] == "John Doe"
    assert response.json()["team_name"] == team_name


def test_update_employee_gpn_already_exists(client):
    team_name = "TEAM_UEC6"
    client.post("/teams/", json={"team_name": team_name})
    client.post("/employees/", json={"gpn": "GPN_UEC6", "employee_name": "Alice Smith", "team_name": team_name})
    client.post("/employees/", json={"gpn": "GPN_UEC7", "employee_name": "John Doe", "team_name": team_name})
    response = client.put("/employees/GPN_UEC6", json={"gpn": "GPN_UEC7", "employee_name": "Davis Smith", "team_name": team_name})
    assert response.status_code == 400


def test_update_employee_gpn_not_provided(client):
    response = client.put("/employees/GPN_UEC8", json={"employee_name": "John Doe", "team_name": "team_uec8"})
    assert response.status_code == 422


def test_update_employee_employee_name_not_provided(client):
    response = client.put("/employees/GPN_UEC9", json={"gpn": "GPN_UEC9", "team_name": "team_uec9"})
    assert response.status_code == 422


def test_delete_employee(client):
    team_name = "TEAM_DED1"
    client.post("/teams/", json={"team_name": team_name})
    client.post("/employees/", json={"gpn": "GPN_DED1", "employee_name": "John Doe", "team_name": team_name})
    response = client.delete("/employees/GPN_DED1")
    assert response.status_code == 200
    assert response.json()["message"] == "Employee deleted successfully"
    response = client.get("/employees/GPN_DED1")
    assert response.status_code == 404


def test_delete_employee_invalid_gpn(client):
    response = client.delete("/employees/GPN_INVALID")
    assert response.status_code == 404
