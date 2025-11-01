from sqlmodel import Session, create_engine

from app.config.settings import get_settings

settings = get_settings()

url = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"

engine = create_engine(url)


def get_db():
    with Session(engine) as db:
        yield db
