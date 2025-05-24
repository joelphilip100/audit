from fastapi import FastAPI
from app.routers import employee
from app.database import engine
from app.models.employee import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(employee.router)