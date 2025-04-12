import asyncio
from models import Base
from database import engine

async def init_models():
    async with engine.begin() as conn:
        # Drop old tables
        await conn.run_sync(Base.metadata.drop_all)
        # Create updated tables
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database updated with new columns (like sentiment)")

# Run the function
asyncio.run(init_models())
