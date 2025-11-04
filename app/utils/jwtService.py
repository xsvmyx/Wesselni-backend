from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt  # type:ignore
from fastapi import HTTPException
from app.config import SECRET_KEY,ALGORITHM
# ========================
# CONFIGURATION
# ========================

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 2  # 2 jours


# ========================
# CRÉATION DU TOKEN
# ========================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crée un token JWT signé avec une date d’expiration."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ========================
# DÉCODAGE DU TOKEN
# ========================

def decode_access_token(token: str) -> dict:
    """Décode un JWT et retourne son contenu, ou lève une exception si invalide."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")


# ========================
# EXTRACTION DES DONNÉES DU TOKEN
# ========================

def get_token_data(token: str) -> dict:
    """Retourne les infos utilisateur (ex: user_id) contenues dans le token."""
    payload = decode_access_token(token)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=401, detail="Token invalide : champ 'sub' manquant")

    return {
        "user_id": user_id,
        "expires_at": payload.get("exp"),
    }
