from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from app.core.config import settings  # usa seu Settings

# ---------------------------
# Bcrypt
# ---------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ---------------------------
# JWT
# ---------------------------
def create_access_token(data: dict, expires_delta: int | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=expires_delta or settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire})

    # ⚠ Converte sub para string
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])

    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def decode_access_token(token: str):
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    return payload
