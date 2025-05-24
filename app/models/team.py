from sqlalchemy import Column, String, Integer
from app.database import Base

class Team(Base):
    __tablename__ = "teams"
    team_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    team_name = Column(String, unique=True, nullable=False)