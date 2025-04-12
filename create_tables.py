from database import engine
from models import Base

# This will create the tables in your database
Base.metadata.create_all(bind=engine)

print("✅ Tables created successfully!")
