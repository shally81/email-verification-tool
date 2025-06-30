from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime, os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///verification.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class VerificationLog(Base):
    __tablename__ = "verifications"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    status = Column(String)
    reason = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)