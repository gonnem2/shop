from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase


engine = create_async_engine(
    "postgresql+asyncpg://postgres:asdqwe@localhost/shop", echo=True
)

SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession)

class Base(DeclarativeBase):
    pass