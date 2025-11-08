from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.auth import verify_password, create_access_token
from app.core.database import get_db
from app.models.user_model import User

router = APIRouter(tags=["Autenticação"])

@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    """
    Login de usuário. Aceita JSON ou form-urlencoded com campos:
    - matricula
    - senha
    """

    # 1️⃣ Tenta ler JSON
    try:
        data = await request.json()
        matricula = data.get("matricula")
        senha = data.get("senha")
    except Exception:
        # 2️⃣ Se JSON falhar, tenta form-urlencoded
        form = await request.form()
        matricula = form.get("matricula")
        senha = form.get("senha")

    # Remove espaços extras
    matricula = matricula.strip() if matricula else None
    senha = senha.strip() if senha else None

    # 3️⃣ Valida campos
    if not matricula or not senha:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Matrícula e senha são obrigatórios"
        )

    # 4️⃣ Busca usuário
    user = db.query(User).filter(User.matricula == matricula).first()
    print("Usuário encontrado:", user)  # debug
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Matrícula ou senha incorreta"
        )

    # 5️⃣ Verifica senha
    if not verify_password(senha, user.senha_hash):
        print("Senha digitada:", senha)
        print("Hash no banco:", user.senha_hash)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Matrícula ou senha incorreta"
        )

    # 6️⃣ Cria token JWT
    token = create_access_token(
        data={
            "sub": user.id,
            "matricula": user.matricula,
            "role": user.tipo_usuario,
            "region": user.regiao
        }
    )

    # 7️⃣ Retorna token
    return {"access_token": token, "token_type": "bearer"}
