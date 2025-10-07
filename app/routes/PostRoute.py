from app.schemas.tokenSchema import Token,TokenInput
from app.schemas.PostSchema import PostCreate, PostResponse
from fastapi import APIRouter, Depends, HTTPException
from app.utils.jwtService import get_token_data
from sqlalchemy.future import select 
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.PostModel import Post
from app.models.UserModel import User
from app.db.database import get_db
from typing import List


router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("/new", response_model=PostResponse)
async def create_post(post_data: PostCreate, db: AsyncSession = Depends(get_db), token: str = ""):
    if not token:
        raise HTTPException(status_code=401, detail="Token required")

    
    try:
        token_info = get_token_data(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

    user_id = int(token_info["user_id"])

    
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    
    new_post = Post(
        title=post_data.title,
        content=post_data.content,
        user_id=user_id
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)

    return new_post


@router.get("/all_posts", response_model=List[PostResponse])
async def get_all_posts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post))
    posts = result.scalars().all()
    return posts



@router.get("/user/{user_id}", response_model=List[PostResponse])
async def get_user_posts(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).filter(Post.user_id == user_id))
    posts = result.scalars().all()
    return posts