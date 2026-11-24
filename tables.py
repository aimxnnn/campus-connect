from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base
from datetime import datetime
import os

os.makedirs("data", exist_ok=True)

engine = create_engine("sqlite:///./data/campus.db", connect_args={"check_same_thread": False})

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="student")
    created_at = Column(DateTime, default=datetime.now)


class Club(Base):
    __tablename__ = "clubs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    category = Column(String, nullable=False)
    coordinator_id = Column(Integer, ForeignKey("users.id"), nullable=False)


class Membership(Base):
    __tablename__ = "memberships"
    __table_args__ = (UniqueConstraint("club_id", "student_id"),)

    id = Column(Integer, primary_key=True, index=True)
    club_id = Column(Integer, ForeignKey("clubs.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.now)


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    club_id = Column(Integer, ForeignKey("clubs.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    venue = Column(String, nullable=False)
    event_date = Column(DateTime, nullable=False)
    deadline = Column(DateTime, nullable=False)
    capacity = Column(Integer, nullable=False)


class Registration(Base):
    __tablename__ = "registrations"
    __table_args__ = (UniqueConstraint("event_id", "student_id"),)

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    attended = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.now)


Base.metadata.create_all(engine)
