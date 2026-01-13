from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True, # set to False in production
    future=True,
    pool_pre_ping=True # verify connections before using
)

# create async factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# base class for models
class Base(DeclarativeBase):
    pass

# dependency injectionn to get db session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()