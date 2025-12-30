from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./complaints.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    reference_id = Column(String, unique=True, index=True)
    complaint_type = Column(String)
    location = Column(String)
    category = Column(String) 
    details = Column(String)
    issue = Column(String)


def init_db():
    Base.metadata.create_all(bind=engine)
