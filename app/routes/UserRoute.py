from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.userSchema import UserCreate, UserLogin
from app.schemas.tokenSchema import Token,TokenInput
from app.services.UserService import create_user, authenticate_user
from app.utils.jwtService import create_access_token,get_token_data

router = APIRouter(tags=["Users"])


@router.post("/register")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    new_user = await create_user(db, user)
    if not new_user:
        raise HTTPException(status_code=401, detail="could not register")

    return {"message": "User added successfully", "user_id": new_user.id}


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, user_data)

    access_token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}





@router.post("/decode_token")
async def decode_token_route(data: TokenInput):
    """
    Prend un token JWT en entrée et retourne les informations décodées.
    """
    try:
        decoded = get_token_data(data.token)
        return {"decoded_token": decoded}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))