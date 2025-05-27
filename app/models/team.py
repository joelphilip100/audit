from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from app.database import Base

class Team(Base):
    __tablename__ = "teams"
    team_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    team_name = Column(String, unique=True, nullable=False)
    
    employees = relationship("Employee", back_populates="team")