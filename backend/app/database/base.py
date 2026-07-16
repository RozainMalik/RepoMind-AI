# Every SQLAlchemy model inherits from this class.

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase): # base is like a parent class for every table in our application
    pass

