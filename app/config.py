import os
from dotenv import load_dotenv # type: ignore

# Charger les variables du fichier .env
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
DATABASE_URL = os.getenv("DATABASE_URL").replace(
    "postgres://", 
    "postgresql+asyncpg://"
).replace(
    "postgresql://",
    "postgresql+asyncpg://"
)


