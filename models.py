from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Chat(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    message = Column(String, nullable=False)
    sentiment = Column(String)  # ✅ Add this line
    timestamp = Column(DateTime, default=datetime.utcnow)
