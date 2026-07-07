from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine( # the create engine connects to the postgresql, means it gives path to the SQLAlchemy where our database is
    settings.DATABASE_URL,
    echo=True, # This prints every SQL query to the terminal.
)

SessionLocal = sessionmaker( # represents a conversation with the database. equest gets its own session, does its work, and then closes it. ensures no interference of users, transaction isolation and smooth rollback
    bind=engine,
    autoflush=False,
    autocommit=False,
)