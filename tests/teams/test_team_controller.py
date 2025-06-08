def test_get_all_teams_returns_empty_list(client):
    response = client.get("/teams/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_all_teams_returns_list_of_teams(client):
    team1_name = "TEAM_RTC1"
    team2_name = "TEAM_RTC2"
    client.post("/teams/", json={"team_name": team1_name}).json()
    client.post("/teams/", json={"team_name": team2_name}).json()

    response = client.get("/teams/")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert any(team["team_name"] == team1_name for team in response.json())
    assert any(team["team_name"] == team2_name for team in response.json())


def test_get_team_by_id(client):
    team_name = "TEAM_RTC3"
    team = client.post("/teams/", json={"team_name": team_name}).json()
    response = client.get("/teams/" + str(team["team_id"]))
    assert response.status_code == 200
    assert response.json()["team_id"] is not None
    assert response.json()["team_name"] == team_name


def test_get_team_by_id_when_team_does_not_exist(client):
    response = client.get("/teams/10000")
    assert response.status_code == 404


def test_create_team(client):
    team_name = "TEAM_CTC1"
    response = client.post("/teams/", json={"team_name": team_name})
    assert response.status_code == 201
    assert response.json()["team_id"] is not None
    assert response.json()["team_name"] == team_name


def test_create_team_when_team_name_already_exists(client):
    team_name = "TEAM_CTC2"
    client.post("/teams/", json={"team_name": team_name}).json()
    response = client.post("/teams/", json={"team_name": team_name})
    assert response.status_code == 400


def test_create_team_team_name_not_provided(client):
    response = client.post("/teams/", json={})
    assert response.status_code == 422


def test_update_team(client):
    team_name = "TEAM_UTC1"
    team = client.post("/teams/", json={"team_name": team_name}).json()
    response = client.put("/teams/" + str(team["team_id"]), json={"team_name": "TEAM_UTC2"})
    assert response.status_code == 200
    assert response.json()["team_id"] is not None
    assert response.json()["team_name"] == "TEAM_UTC2"


def test_update_team_when_team_does_not_exist(client):
    response = client.put("/teams/10000", json={"team_name": "TEAM_UTC3"})
    assert response.status_code == 404


def test_update_team_team_name_not_provided(client):
    team_name = "TEAM_UTC1"
    team = client.post("/teams/", json={"team_name": team_name}).json()
    response = client.put("/teams/" + str(team["team_id"]), json={})
    assert response.status_code == 422


def test_delete_employee(client):
    team_name = "TEAM_DED1"
    team = client.post("/teams/", json={"team_name": team_name}).json()
    response = client.delete("/teams/" + str(team["team_id"]))
    assert response.status_code == 200
    assert response.json()["message"] == "Team deleted successfully"
    response = client.get("/teams/" + str(team["team_id"]))
    assert response.status_code == 404


def test_delete_team_when_team_does_not_exist(client):
    response = client.delete("/teams/10000")
    assert response.status_code == 404
