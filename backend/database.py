from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/hcp_crm")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_name = Column(String(255), nullable=True)
    interaction_type = Column(String(100), nullable=True, default="Meeting")
    date = Column(String(20), nullable=True)
    time = Column(String(20), nullable=True)
    attendees = Column(Text, nullable=True)
    topics_discussed = Column(Text, nullable=True)
    materials_shared = Column(JSON, nullable=True, default=list)
    samples_distributed = Column(JSON, nullable=True, default=list)
    sentiment = Column(String(50), nullable=True, default="Neutral")
    outcomes = Column(Text, nullable=True)
    follow_up_actions = Column(Text, nullable=True)
    ai_suggested_followups = Column(JSON, nullable=True, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class HCP(Base):
    __tablename__ = "hcps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    specialty = Column(String(255), nullable=True)
    hospital = Column(String(255), nullable=True)
    city = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    # Seed some HCP data
    db = SessionLocal()
    try:
        if db.query(HCP).count() == 0:
            sample_hcps = [
                HCP(name="Dr. Smith", specialty="Oncology", hospital="City General Hospital", city="New York"),
                HCP(name="Dr. John", specialty="Cardiology", hospital="Metro Heart Center", city="Boston"),
                HCP(name="Dr. Sharma", specialty="Nephrology", hospital="Apollo Hospital", city="Chicago"),
                HCP(name="Dr. Patel", specialty="Endocrinology", hospital="University Medical Center", city="Houston"),
                HCP(name="Dr. Williams", specialty="Gastroenterology", hospital="Regional Medical Center", city="Dallas"),
            ]
            db.add_all(sample_hcps)
            db.commit()
    finally:
        db.close()