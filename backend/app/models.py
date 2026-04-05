from sqlalchemy import Column, Integer, Float, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    telegram_alias = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    excursions = Column(Integer, default=0)

    def __repr__(self):
        return f"<User(id={self.id}, telegram=@{self.telegram_alias})>"


class Excursion(Base):
    __tablename__ = "excursions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
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
        return f"<Excursion(id={self.id}, user_id={self.user_id}, tourists={self.number_of_tourists})>"
