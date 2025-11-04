from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATABASE_URL







engine = create_async_engine(DATABASE_URL, echo=True, future=True)



AsyncSessionLocal = sessionmaker(
engine,
class_=AsyncSession,
expire_on_commit=False,
autoflush=False,
)



Base = declarative_base()




async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session




async def init_db() -> None:

    async with engine.begin() as conn:

        await conn.run_sync(Base.metadata.create_all)