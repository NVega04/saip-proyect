from sqlmodel import create_engine, SQLModel, Session

from src.core.config import settings

mysql_url = settings.mysql_url

engine = create_engine(mysql_url, echo=settings.sqlalchemy_echo)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
