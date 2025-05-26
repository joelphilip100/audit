from fastapi import FastAPI
from app.routers import employee, team
from app.database import engine
from app.models.employee import Base
from app.middleware import log_requests

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.middleware("http")(log_requests)
app.include_router(employee.router)
app.include_router(team.router)