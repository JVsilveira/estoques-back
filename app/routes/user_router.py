from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.dependencies import get_db
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserResponse, UserUpdate
from app.core.auth import get_password_hash
import unicodedata

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"]
)

# -------------------------
# Função auxiliar
# -------------------------
def normalize_string(s: str) -> str:
    """Remove acentos e transforma em lowercase"""
    return unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode("utf-8").lower()

# -------------------------
# Criar usuário
# -------------------------
@router.post("/", response_model=UserResponse)
def criar_usuario(user: UserCreate, db: Session = Depends(get_db)):
    usuario_existente = db.query(User).filter(User.matricula == user.matricula).first()
    if usuario_existente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Matrícula já cadastrada")

    novo_usuario = User(
        nome=user.nome,  # nome com acento e capitalização
        matricula=user.matricula,
        senha_hash=get_password_hash(user.senha),
        cargo=user.cargo,
        regiao=user.regiao,
        tipo_usuario=user.tipo_usuario,
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario

# -------------------------
# Listar usuários com busca aproximada
# -------------------------
@router.get("/", response_model=list[UserResponse])
def listar_usuarios(nome: str = "", db: Session = Depends(get_db)):
    if not nome:
        return []  # tabela inicia vazia
    
    nome_norm = normalize_string(nome)
    
    usuarios = db.query(User).filter(
        func.lower(func.unaccent(User.nome)).ilike(f"%{nome_norm}%")
    ).all()
    return usuarios

# -------------------------
# Atualizar usuário
# -------------------------
@router.put("/{matricula}", response_model=UserResponse)
def atualizar_usuario(matricula: str, dados: UserUpdate, db: Session = Depends(get_db)):
    usuario = db.query(User).filter(User.matricula == matricula).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if dados.senha:
        usuario.senha_hash = get_password_hash(dados.senha)
    if dados.nome:
        usuario.nome = dados.nome  
    if dados.cargo:
        usuario.cargo = dados.cargo
    if dados.regiao:
        usuario.regiao = dados.regiao
    if dados.tipo_usuario:
        usuario.tipo_usuario = dados.tipo_usuario

    db.commit()
    db.refresh(usuario)
    return usuario

# -------------------------
# Deletar usuário
# -------------------------
@router.delete("/{matricula}", status_code=204)
def deletar_usuario(matricula: str, db: Session = Depends(get_db)):
    usuario = db.query(User).filter(User.matricula == matricula).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    db.delete(usuario)
    db.commit()
    return {"detail": "Usuário deletado com sucesso"}
