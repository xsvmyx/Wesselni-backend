from fastapi import APIRouter, UploadFile, File, HTTPException, Header, Depends
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import get_db
from app.utils.jwtService import get_token_data
from app.models.UserModel import User

router = APIRouter(prefix="/uploads", tags=["uploads"])

@router.post("/setpfp")
async def set_profile_picture(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    authorization: str = Header(...),
):
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")

    token = authorization.replace("Bearer ", "")
    token_info = get_token_data(token)
    user_id = token_info.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or missing token")

    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

   
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    #Nom du fichier basé sur l'ID de l'utilisateur
    ext = os.path.splitext(file.filename)[1]
    filename = f"user_{user_id}{ext}"
    path = os.path.join(upload_dir, filename)

    try:
        
        with open(path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    
    image_url = f"/uploads/{filename}"

    # Mise à jour du champ 'doc' dans la table User
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
