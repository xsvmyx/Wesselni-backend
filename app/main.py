from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes import UserRoute,PostRoute  # ton fichier avec le endpoint register

@asynccontextmanager
async def lifespan(app: FastAPI):
    # code du startup
    try:
        yield
    finally:
        pass

app = FastAPI(lifespan=lifespan)

app.include_router(UserRoute.router)
app.include_router(PostRoute.router)



@app.get("/")
def read_root():
    return {"message": "Bienvenue sur Wesselni!"}
