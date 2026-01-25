from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes import UserRoute, PostRoute, ImagesRoute
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type:ignore
from datetime import datetime, timedelta, timezone
from app.models.PostModel import Post
from app.db.database import AsyncSessionLocal
from sqlalchemy.future import select
from sqlalchemy import text


async def delete_old_posts():
    async with AsyncSessionLocal() as db:
        threshold = datetime.now(timezone.utc) - timedelta(hours=24)
        result = await db.execute(select(Post).filter(Post.created_at < threshold))
        old_posts = result.scalars().all()

        for post in old_posts:
            await db.delete(post)

        await db.commit()

        if old_posts:
            print(f"🧹 {len(old_posts)} old posts deleted automatically.")


scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(delete_old_posts, "interval", hours=24)
    scheduler.start()
    print("✅ APScheduler started")

    try:
        yield
    finally:
        scheduler.shutdown(wait=False)
        print("🛑 APScheduler stopped")


app = FastAPI(lifespan=lifespan)

app.include_router(UserRoute.router)
app.include_router(PostRoute.router)
app.include_router(ImagesRoute.router)


@app.get("/")
def read_root():
    return {"message": "Bienvenue sur Wesselni!"}


@app.get("/keepalive")
@app.head("/keepalive") #uptimerobot use head requests for free
async def keepalive():
    """Endpoint pour garder Supabase Postgres actif (éviter sommeil après 7j)"""
    try:
        async with AsyncSessionLocal() as db:
            # Requête simple pour ping la DB
            await db.execute(text("SELECT 1"))
            await db.commit()
        
        return {
            "status": "ok",
            "message": "Supabase DB active",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }