from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import get_db, get_current_user
from app.models.ativo_model import Ativo
from app.schemas.ativo_schema import AtivoCreate, AtivoResponse, AtivoUpdate

router = APIRouter(prefix="/ativos", tags=["Ativos"])

@router.post("/", response_model=AtivoResponse)
def criar_ativo(item: AtivoCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    regiao = user.regiao if getattr(user, "regiao", None) else "GERAL"

    novo_ativo = Ativo(**item.dict(), regiao=regiao)
    db.add(novo_ativo)
    db.commit()
    db.refresh(novo_ativo)
    return novo_ativo

@router.get("/", response_model=List[AtivoResponse])
def listar_ativos(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if getattr(user, "regiao", None):
        return db.query(Ativo).filter(Ativo.regiao == user.regiao).all()
    return db.query(Ativo).all()

@router.put("/{ativo_id}", response_model=AtivoResponse)
def atualizar_ativo(ativo_id: int, dados: AtivoUpdate, db: Session = Depends(get_db)):
    ativo = db.query(Ativo).filter(Ativo.id == ativo_id).first()
    if not ativo:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
    for campo, valor in dados.dict(exclude_unset=True).items():
        setattr(ativo, campo, valor)
    db.commit()
    db.refresh(ativo)
    return ativo

@router.delete("/{ativo_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_ativo(ativo_id: int, db: Session = Depends(get_db)):
    ativo = db.query(Ativo).filter(Ativo.id == ativo_id).first()
    if not ativo:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
    db.delete(ativo)
    db.commit()