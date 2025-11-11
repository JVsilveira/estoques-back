from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import get_db, get_current_user
from app.models.periferico_model import Periferico
from app.schemas.periferico_schema import PerifericoCreate, PerifericoResponse, PerifericoUpdate

router = APIRouter(prefix="/ativos", tags=["Ativos"])

@router.post("/", response_model=PerifericoCreate)
def criar_periferico(item: PerifericoCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    regiao = user.regiao if getattr(user, "regiao", None) else "GERAL"

    novo_periferico = Periferico(**item.dict(), regiao=regiao)
    db.add(novo_periferico)
    db.commit()
    db.refresh(novo_periferico)
    return novo_periferico

@router.get("/", response_model=List[PerifericoResponse])
def listar_perifericos(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if getattr(user, "regiao", None):
        return db.query(Periferico).filter(Periferico.regiao == user.regiao).all()
    return db.query(Periferico).all()

@router.put("/{periferico_id}", response_model=PerifericoResponse)
def atualizar_periferico(periferico_id: int, dados: PerifericoUpdate, db: Session = Depends(get_db)):
    periferico = db.query(Periferico).filter(Periferico.id == periferico_id).first()
    if not periferico:
        raise HTTPException(status_code=404, detail="Periférico não encontrado")
    for campo, valor in dados.dict(exclude_unset=True).items():
        setattr(periferico, campo, valor)
    db.commit()
    db.refresh(periferico)
    return periferico

@router.delete("/{periferico_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_periferico(periferico_id: int, db: Session = Depends(get_db)):
    periferico = db.query(Periferico).filter(Periferico.id == periferico_id).first()
    if not periferico:
        raise HTTPException(status_code=404, detail="Periférico não encontrado")
    db.delete(periferico)
    db.commit()