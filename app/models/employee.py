from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Employee(Base):
    __tablename__ = "employees"
    employee_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    gpn = Column(String, nullable=False, unique=True)
    employee_name = Column(String, nullable=False)

    team_id = Column(Integer, ForeignKey("teams.team_id", ondelete="SET NULL"), nullable=True)
    team = relationship("Team", back_populates="employees")

    @property
    def team_name(self):
        return self.team.team_name if self.team else None
    
    