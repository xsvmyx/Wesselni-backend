from app.schemas.tokenSchema import Token,TokenInput
from app.schemas.PostSchema import PostCreate, PostResponse , PostUserResponse
from fastapi import APIRouter, Depends, HTTPException
from app.utils.jwtService import get_token_data
from sqlalchemy.future import select 
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.PostModel import Post
from app.models.UserModel import User
from app.db.database import get_db
from typing import List


router = APIRouter(prefix="/posts", tags=["Posts"])

#le mapping est automatique entre l'objet Post et PostResponse 
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
        departure = post_data.departure,
        destination= post_data.destination,
        departure_time=post_data.departure_time,
        details = post_data.details,
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


@router.delete("/delete/{post_id}")
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = ""
):
    
    if not token:
        raise HTTPException(status_code=401, detail="Token required")

    
    try:
        token_info = get_token_data(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

    user_id = int(token_info["user_id"])

    
    result = await db.execute(select(Post).filter(Post.id == post_id))
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

   
    if post.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")

    
    await db.delete(post)
    await db.commit()

    return {"message": "Post deleted successfully"}


@router.get("/search", response_model=List[PostResponse])
async def search_posts(
    departure: str,
    destination: str,
    db: AsyncSession = Depends(get_db)
):
   
    result = await db.execute(
        select(Post).filter(
            Post.departure.ilike(f"%{departure}%"),
            Post.destination.ilike(f"%{destination}%")
        )
    )

    posts = result.scalars().all()

    if not posts:
        raise HTTPException(status_code=404, detail="No posts found")

    return posts




@router.get("/feed", response_model=List[PostUserResponse])
async def get_posts_with_users(db: AsyncSession = Depends(get_db)):
    query = (
        select(
            User.id.label("id_user"),
            Post.departure,
            Post.destination,
            Post.departure_time,
            User.phone,
            Post.details,
            User.doc
        )
        .join(User, User.id == Post.user_id)
    )

    result = await db.execute(query)
    rows = result.all()

    # convertir les résultats en dicts pour Pydantic
    return [
        {
            "id_user": r.id_user,
            "departure": r.departure,
            "destination": r.destination,
            "departure_time": r.departure_time,
            "phone": r.phone,
            "details": r.details,
            "doc": r.doc,
        }
        for r in rows
    ]