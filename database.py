from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os

DATABASE_URL = "postgresql+asyncpg://chatbot_db_h3yo_user:VwuhelgMr1s7zyYBPwUBXbVbEDKhpvev@dpg-cvo1qingi27c73bqq1hg-a.oregon-postgres.render.com/chatbot_db_h3yo"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

# This function is used as a dependency in FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
