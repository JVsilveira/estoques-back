from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserResponse, UserUpdate
from app.core.auth import get_password_hash

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"]
)

@router.post("/", response_model=UserResponse)
def criar_usuario(user: UserCreate, db: Session = Depends(get_db)):
    usuario_existente = db.query(User).filter(User.matricula == user.matricula).first()
    if usuario_existente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Matrícula já cadastrada")

    novo_usuario = User(
        nome=user.nome,
        matricula=user.matricula,
        senha_hash=get_password_hash(user.senha),
        cargo=user.cargo,
        regiao=user.regiao,
        tipo_usuario=user.tipo_usuario
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario

@router.get("/", response_model=list[UserResponse])
def listar_usuarios(nome: str = "", db: Session = Depends(get_db)):
    usuarios = db.query(User).filter(User.nome.ilike(f"%{nome}%")).all()
    return usuarios

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

@router.delete("/{matricula}", status_code=204)
def deletar_usuario(matricula: str, db: Session = Depends(get_db)):
    usuario = db.query(User).filter(User.matricula == matricula).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    db.delete(usuario)
    db.commit()
    return {"detail": "Usuário deletado com sucesso"}