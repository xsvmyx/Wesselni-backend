from app.schemas.tokenSchema import Token,TokenInput
from app.schemas.PostSchema import PostCreate, PostResponse , PostUserResponse
from fastapi import APIRouter, Depends, HTTPException,Query,Header
from app.utils.jwtService import get_token_data
from sqlalchemy.future import select 
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.PostModel import Post
from app.models.UserModel import User
from app.db.database import get_db
from typing import List


router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("/new_post", response_model=PostResponse)
async def create_post(
    post_data: PostCreate,
    db: AsyncSession = Depends(get_db),
    authorization: str = Header(...),  
):

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Format de token invalide")

    token = authorization.replace("Bearer ", "")
    token_info = get_token_data(token)

    user_id = token_info.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token invalide ou manquant")

    result = await db.execute(select(User).filter(User.id == int(user_id)))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    new_post = Post(
        departure=post_data.departure,
        destination=post_data.destination,
        departure_time=post_data.departure_time,
        details=post_data.details,
        user_id=int(user_id)
    )

    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)


    return new_post


####################################################################
@router.get("/user/{user_id}", response_model=List[PostUserResponse])
async def get_user_posts(user_id: int, db: AsyncSession = Depends(get_db)):
    query = (
        select(
            Post.id,
            User.id.label("id_user"),
            Post.departure,
            Post.destination,
            Post.departure_time,
            User.phone,
            Post.details,
            User.doc
        )
        .join(User, User.id == Post.user_id)
        .filter(Post.user_id == user_id)
        .order_by(Post.created_at.desc())
    )

    result = await db.execute(query)
    rows = result.all()

    # convertir les résultats en dicts pour Pydantic
    return [
        {
            "id_post":r.id,
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


##############################################################################


@router.delete("/delete/{post_id}")
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    authorization: str = Header(...),  
):
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Format de token invalide")

    token = authorization.replace("Bearer ", "")
    
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


# @router.get("/feed", response_model=List[PostUserResponse])
# async def get_posts_with_users(db: AsyncSession = Depends(get_db)):
#     query = (
#         select(
#             Post.id,
#             User.id.label("id_user"),
#             Post.departure,
#             Post.destination,
#             Post.departure_time,
#             User.phone,
#             Post.details,
#             User.doc
#         )
#         .join(User, User.id == Post.user_id)
#         .order_by(Post.created_at.desc())
#     )

#     result = await db.execute(query)
#     rows = result.all()

#     # convertir les résultats en dicts pour Pydantic
#     return [
#         {
#             "id_post":r.id,
#             "id_user": r.id_user,
#             "departure": r.departure,
#             "destination": r.destination,
#             "departure_time": r.departure_time,
#             "phone": r.phone,
#             "details": r.details,
#             "doc": r.doc,
#         }
#         for r in rows
#     ]



@router.get("/feed", response_model=List[PostUserResponse])
async def get_posts_with_users(
    db: AsyncSession = Depends(get_db),
    authorization: str = Header(...),  
    limit: int = Query(4, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Format de token invalide")

    token = authorization.replace("Bearer ", "")
    
    try:
        token_data = get_token_data(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token invalide: {str(e)}")

    # Optionnel : si tu veux t’assurer que l’utilisateur existe toujours
    user_id = token_data.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token invalide ou manquant")

    #  Récupération des posts
    query = (
        select(
            Post.id,
            User.id.label("id_user"),
            Post.departure,
            Post.destination,
            Post.departure_time,
            User.phone,
            Post.details,
            User.doc,
        )
        .join(User, User.id == Post.user_id)
        .order_by(Post.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(query)
    rows = result.all()

    return [
        {
            "id_post": r.id,
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







@router.get("/user")
async def get_user_by_id(
    user_id: int = Query(...),
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    
    token = authorization.replace("Bearer ", "")
    
    try:
        get_token_data(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "nom": user.nom,
        "prenom": user.prenom,
        "wilaya": user.wilaya,
        "commune": user.commune,
        "telephone": user.phone,
        "doc":user.doc if user.doc else None
    }



@router.get("/search")
async def search_posts(query: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Post)
        .filter(Post.destination.ilike(f"%{query}%"))
    )
    posts = result.scalars().all()
    return posts







@router.get("/search/suggestions")
async def search_suggestions(
    query: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db)
):
    
    if not query.strip():
        return []

    stmt = (
        select(Post.id, Post.departure, Post.destination, Post.departure_time)
        .where(Post.destination.ilike(f"%{query}%"))
        .limit(10)
    )

    result = await db.execute(stmt)
    posts = result.mappings().all()  
    return posts