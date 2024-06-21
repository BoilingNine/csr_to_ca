from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base

from settings import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, DEBUG

SQLALCHEMY_DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=DEBUG, future=True, pool_pre_ping=True)
SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(autocommit=False, autoflush=False, bind=engine,
                                                                    expire_on_commit=False)
Base = declarative_base()


class DBBase(Base):
    __abstract__ = True

    async def to_dict(self):
        db_dict = self.__dict__.copy()
        del db_dict['_sa_instance_state']
        return db_dict
