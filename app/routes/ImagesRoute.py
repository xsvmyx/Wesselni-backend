from fastapi import APIRouter, UploadFile, File, HTTPException,Header
import os
import uuid
from app.utils.jwtService import get_token_data

router = APIRouter(prefix="/uploads", tags=["uploads"])

@router.post("/setpfp")
async def set_profile_picture(
    file: UploadFile = File(...),
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

    
    ext = os.path.splitext(file.filename)[1]
    filename = f"user_{user_id}{ext}"
    path = os.path.join(upload_dir, filename)

    try:
        
        with open(path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    
    return {"url": f"/uploads/{filename}"}