from sqlalchemy import Column, String, Integer
from app.database import Base

class Employee(Base):
    __tablename__ = "employees"
    employee_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    gpn = Column(String, nullable=False, unique=True)
    employee_name = Column(String, nullable=False)
    team_name = Column(String, nullable=False)