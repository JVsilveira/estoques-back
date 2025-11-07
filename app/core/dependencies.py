from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.auth import decode_access_token
from app.core.database import SessionLocal
from app.models.user_model import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ---------------------------
# Sessão do banco
# ---------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------
# Usuário atual
# ---------------------------
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    user_id = payload.get("sub") or payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    # Atualiza role e região se estiverem no token
    if "role" in payload:
        user.role = payload["role"].lower()
    if "regiao" in payload:
        user.region = payload["regiao"]

    return user

# ---------------------------
# Filtragem de ativos por usuário
# ---------------------------
def filter_ativos_by_user(db: Session, current_user: User):
    """
    Usuário admin: retorna todos os ativos.
    Usuário comum: retorna apenas ativos da sua região.
    """
    from app.models.ativo_model import Ativo

    query = db.query(Ativo)
    if current_user.role != "admin" and current_user.region:
        query = query.filter(Ativo.region == current_user.region)
    return query.all()
