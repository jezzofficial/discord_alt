# app/database.py

from sqlmodel import create_engine, Session

DATABASE_URL = "sqlite:///./test.db"  # для начала SQLite

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
