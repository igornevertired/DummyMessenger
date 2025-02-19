# models.py
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    text = Column(String, nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    user_message_count = Column(Integer, nullable=False)
