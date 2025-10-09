import os
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.data.models import BaseEntity


db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise ValueError("DATABASE_URL is not set!")

engine = create_async_engine(url=db_url)
async_session = async_sessionmaker(engine)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(BaseEntity.metadata.create_all)
