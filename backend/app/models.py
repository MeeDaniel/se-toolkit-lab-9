from sqlalchemy import Column, Integer, Float, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class Excursion(Base):
    __tablename__ = "excursions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    number_of_tourists = Column(Integer, nullable=False)
    average_age = Column(Float, nullable=False)
    age_distribution = Column(Float, nullable=True)
    vivacity_before = Column(Float, nullable=False)
    vivacity_after = Column(Float, nullable=False)
    interest_in_it = Column(Float, nullable=False)
    interests_list = Column(Text, nullable=True)  # Space-separated keywords
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    raw_message = Column(Text, nullable=True)  # Original AI message

    def __repr__(self):
        return f"<Excursion(id={self.id}, tourists={self.number_of_tourists}, avg_age={self.average_age})>"
