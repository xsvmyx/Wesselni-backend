from passlib.context import CryptContext # type:ignore


pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],  
    deprecated="auto"
)

def hash_password(plain_password: str) -> str:
    """
    Hash un mot de passe en utilisant pbkdf2_sha256.
    """
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie qu'un mot de passe correspond au hash stocké.
    """
    return pwd_context.verify(plain_password, hashed_password)
