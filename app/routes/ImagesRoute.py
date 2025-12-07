from fastapi import APIRouter, UploadFile, File, HTTPException, Header, Depends
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import get_db
from app.utils.jwtService import get_token_data
from app.models.UserModel import User
from supabase import create_client
from app.config import SUPABASE_URL, SERVICE_ROLE_KEY, BUCKET_NAME

router = APIRouter(prefix="/uploads", tags=["uploads"])

supabase = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)
 

@router.post("/setpfp")
async def set_profile_picture(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    authorization: str = Header(...),
):
    # Vérification du token
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")

    token = authorization.replace("Bearer ", "")
    token_info = get_token_data(token)
    user_id = token_info.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or missing token")

    # Vérifier le type de fichier
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Lire le fichier
    file_bytes = await file.read()
    ext = os.path.splitext(file.filename)[1]
    filename = f"user_{user_id}{ext}"

    # Upload sur Supabase
    response = supabase.storage.from_(BUCKET_NAME).upload(
        filename, file_bytes,
        {"cacheControl": "3600", "upsert": "true"}
    )

    # Check erreur
    error = getattr(response, "error", None) or getattr(response, "error_message", None)
    if error:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {error}")



    # Récupérer l'URL publique
    image_url = supabase.storage.from_(BUCKET_NAME).get_public_url(filename)

    # Mettre à jour l'utilisateur dans la DB
    result = await db.execute(select(User).filter(User.id == int(user_id)))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.doc = image_url
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {
        "message": "Profile picture updated successfully",
        "url": image_url,
    }


