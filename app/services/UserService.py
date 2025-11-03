from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from app.models.UserModel import User
from app.schemas.userSchema import UserCreate, UserLogin ,UserUpdate
from app.utils.encoder import hash_password, verify_password


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    result = await db.execute(select(User).filter(User.phone == user_data.phone))
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(status_code=400, detail="This phone number is already used")

    new_user = User(
        nom=user_data.nom,
        prenom=user_data.prenom,
        phone=user_data.phone,
        password=hash_password(user_data.password),
        wilaya=user_data.wilaya,
        commune=user_data.commune,
        doc=user_data.doc
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


async def find_user(db: AsyncSession, user_data: UserLogin) -> User:
    result = await db.execute(select(User).filter(User.phone == user_data.phone))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect phone number or password")
    return user


async def authenticate_user(db: AsyncSession, user_data: UserLogin) -> User:
    result = await db.execute(select(User).filter(User.phone == user_data.phone))
    user = result.scalars().first()

    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect phone number or password")

    return user




async def update_user_info(db: AsyncSession, user_id: int, user_data: UserUpdate):
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # Appliquer les changements
    user.wilaya = user_data.wilaya
    user.commune = user_data.commune

    await db.commit()
    await db.refresh(user)

    return user



async def delete_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    await db.delete(user)
    await db.commit()

    return {"message": "Utilisateur et ses publications supprimés avec succès"}