from sqlmodel import Session, create_engine

from app.config.settings import get_settings

settings = get_settings()

engine = create_engine(settings.db_connection_string)


def get_db():
    """Get the database session."""
    with Session(engine) as db:
        yield db
