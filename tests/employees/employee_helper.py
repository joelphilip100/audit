from app.teams import models as team_models
from app.employees import models as employee_models


def create_test_team(team_name, test_db) -> team_models.Team:
    team = team_models.Team(team_name=team_name.upper())
    test_db.add(team)
    test_db.commit()
    test_db.refresh(team)
    return team


def create_test_employee(gpn, employee_name, team_name, test_db) -> tuple[employee_models.Employee, team_models.Team]:
    team = create_test_team(team_name, test_db)
    employee = employee_models.Employee(
        gpn=gpn,
        employee_name=employee_name,
        team_id=team.team_id
    )
    test_db.add(employee)
    test_db.commit()
    test_db.refresh(employee)
    return employee, team
