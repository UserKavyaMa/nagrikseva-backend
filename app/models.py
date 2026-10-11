from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
import enum
import datetime

Base = declarative_base()

class ComplaintStatus(str, enum.Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"

class Complaint(Base):
    __tablename__ = "complaints"
    id = Column(Integer, primary_key=True, index=True)
    citizen_name = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    language = Column(String, nullable=False)
    translated_text = Column(Text, nullable=True)
    category = Column(String, nullable=True)
    urgency = Column(Integer, nullable=True)
    sentiment = Column(String, nullable=True)
    status = Column(Enum(ComplaintStatus), default=ComplaintStatus.PENDING)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    location_lat = Column(Float, nullable=True)
    location_lng = Column(Float, nullable=True)
    audio_file_path = Column(String, nullable=True)
