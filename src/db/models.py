# models.py
import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    text = Column(String(1000), nullable=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    count = Column(Integer, default=0)
