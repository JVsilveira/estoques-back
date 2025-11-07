from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.auth import verify_password, create_access_token
from app.core.config import settings 

from app.core.database import get_db
from app.models.user_model import User


router = APIRouter(
    tags=["Autenticação"]
)

@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    """
    Login de usuário. Aceita JSON ou form-urlencoded com campos:
    - matricula
    - senha
    """
    try:
        # Tenta ler como JSON
        data = await request.json()
        matricula = data.get("matricula")
        senha = data.get("senha")
    except:
        # Se falhar, tenta form-urlencoded
        form = await request.form()
        matricula = form.get("matricula")
        senha = form.get("senha")

    if not matricula or not senha:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Matrícula e senha são obrigatórios"
        )

    # Busca usuário pelo campo "matricula"
    user = db.query(User).filter(User.matricula == matricula).first()
    if not user or not verify_password(senha, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Matrícula ou senha incorreta"
        )

    # Cria token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={
            "sub": user.id,
            "role": user.tipo_usuario,
            "region": user.regiao
        },
    )

    return {"access_token": token, "token_type": "bearer"}
