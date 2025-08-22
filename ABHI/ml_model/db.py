# db.py
import os
from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine & session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Feedback Review Table
class FeedbackReview(Base):
    __tablename__ = "feedback_review"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    url = Column(String)
    issue = Column(String)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

# Review Table (like review.csv)
class Review(Base):
    __tablename__ = "review"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    label = Column(Integer)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

# Initialize tables
def init_db():
    Base.metadata.create_all(bind=engine)

# Insert functions
def insert_feedback_review(name, email, url, issue):
    session = SessionLocal()
    new_feedback = FeedbackReview(name=name, email=email, url=url, issue=issue)
    session.add(new_feedback)
    session.commit()
    session.close()

def insert_review(url, label):
    session = SessionLocal()
    new_review = Review(url=url, label=label)
    session.add(new_review)
    session.commit()
    session.close()
