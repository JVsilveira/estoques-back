from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.dependencies import get_db, get_current_user
from app.models.periferico_model import Periferico
from app.schemas.periferico_schema import (
    PerifericoCreate,
    PerifericoResponse,
    PerifericoUpdate
)

router = APIRouter(prefix="/perifericos", tags=["Periféricos"])


# =========================================================
# CRIAR OU ATUALIZAR PERIFÉRICO (UPSERT POR TIPO + REGIÃO)
# =========================================================
@router.post("/", response_model=PerifericoResponse)
def criar_ou_atualizar_periferico(
    item: PerifericoCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    contexto = item.contexto.value
    regiao = user.regiao if getattr(user, "regiao", None) else "GERAL"

    tipo_item = item.tipo_item.strip().upper()

    if item.quantidade <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantidade deve ser maior que zero"
        )

    periferico = (
        db.query(Periferico)
        .filter(
            Periferico.tipo_item == tipo_item,
            Periferico.regiao == regiao
        )
        .first()
    )

    # ======================
    # SAÍDA → SUBTRAI
    # ======================
    if contexto == "SAIDA":
        if not periferico:
            raise HTTPException(
                status_code=404,
                detail="Periférico não encontrado para saída"
            )

        if periferico.quantidade < item.quantidade:
            raise HTTPException(
                status_code=400,
                detail=f"Quantidade insuficiente ({periferico.quantidade} disponíveis)"
            )

        periferico.quantidade -= item.quantidade
        db.commit()
        db.refresh(periferico)
        return periferico

    # ======================
    # ENTRADA → SOMA / CRIA
    # ======================
    if periferico:
        periferico.quantidade += item.quantidade
        db.commit()
        db.refresh(periferico)
        return periferico

    novo_periferico = Periferico(
        tipo_item=tipo_item,
        quantidade=item.quantidade,
        regiao=regiao
    )

    db.add(novo_periferico)
    db.commit()
    db.refresh(novo_periferico)
    return novo_periferico

# =========================================================
# LISTAR PERIFÉRICOS
# =========================================================
@router.get("/", response_model=List[PerifericoResponse])
def listar_perifericos(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if getattr(user, "regiao", None):
        return db.query(Periferico).filter(
            Periferico.regiao == user.regiao
        ).all()

    return db.query(Periferico).all()


# =========================================================
# ATUALIZAR PERIFÉRICO POR ID (MANUAL)
# =========================================================
@router.put("/{periferico_id}", response_model=PerifericoResponse)
def atualizar_periferico(
    periferico_id: int,
    dados: PerifericoUpdate,
    db: Session = Depends(get_db)
):
    periferico = db.query(Periferico).filter(
        Periferico.id == periferico_id
    ).first()

    if not periferico:
        raise HTTPException(
            status_code=404,
            detail="Periférico não encontrado"
        )

    for campo, valor in dados.dict(exclude_unset=True).items():
        setattr(periferico, campo, valor)

    db.commit()
    db.refresh(periferico)
    return periferico


# =========================================================
# DELETAR PERIFÉRICO
# =========================================================
@router.delete("/{periferico_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_periferico(
    periferico_id: int,
    db: Session = Depends(get_db)
):
    periferico = db.query(Periferico).filter(
        Periferico.id == periferico_id
    ).first()

    if not periferico:
        raise HTTPException(
            status_code=404,
            detail="Periférico não encontrado"
        )

    db.delete(periferico)
    db.commit()
