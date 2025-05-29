from fastapi import FastAPI
from app.employees import controller as employee_controller 
from app.teams import controller as team_controller
from app.database import engine, Base
from app.middleware import log_requests

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.middleware("http")(log_requests)
app.include_router(employee_controller.router)
app.include_router(team_controller.router)