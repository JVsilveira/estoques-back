from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.dependencies import get_db, get_current_user
from app.models.ativo_model import Ativo, StatusItem
from app.schemas.ativo_schema import AtivoCreate, AtivoResponse, AtivoUpdate

router = APIRouter(prefix="/ativos", tags=["Ativos"])


def normalizar_str(valor: str | None):
    return valor.strip().upper() if valor else valor


def resolver_status_por_contexto(contexto: str) -> StatusItem:
    contexto = contexto.upper()

    if contexto == "ENTRADA":
        return StatusItem.EM_ESTOQUE
    elif contexto == "SAIDA":
        return StatusItem.EM_USO
    else:
        raise HTTPException(
            status_code=400,
            detail="Contexto inválido. Use ENTRADA ou SAIDA."
        )


# =========================================================
# CRIAR OU ATUALIZAR ATIVO (UPSERT POR NÚMERO DE SÉRIE)
# =========================================================
@router.post("/", response_model=AtivoResponse)
def criar_ou_atualizar_ativo(
    item: AtivoCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # =========================================================
    # CONTEXTO
    # =========================================================
    contexto = item.contexto.upper()
    status_resolvido = resolver_status_por_contexto(contexto)

    # =========================================================
    # REGIÃO (REGRA FINAL)
    # =========================================================
    if item.regiao:
        regiao_final = item.regiao.upper()

    elif getattr(user, "regiao", None):
        regiao_final = user.regiao.upper()

    else:
        raise HTTPException(
            status_code=400,
            detail="Região obrigatória para administrador"
        )

    numero_serie_normalizado = normalizar_str(item.numero_serie)

    ativo_existente = (
        db.query(Ativo)
        .filter(Ativo.numero_serie == numero_serie_normalizado)
        .first()
    )

    # =========================================================
    # UPDATE
    # =========================================================
    if ativo_existente:
        ativo_existente.tipo_item = normalizar_str(item.tipo_item)
        ativo_existente.marca = normalizar_str(item.marca)
        ativo_existente.modelo = normalizar_str(item.modelo)
        ativo_existente.nota_fiscal = normalizar_str(item.nota_fiscal)
        ativo_existente.regiao = regiao_final
        ativo_existente.status = status_resolvido

        db.commit()
        db.refresh(ativo_existente)
        return ativo_existente

    # =========================================================
    # CREATE
    # =========================================================
    novo_ativo = Ativo(
        tipo_item=normalizar_str(item.tipo_item),
        marca=normalizar_str(item.marca),
        modelo=normalizar_str(item.modelo),
        nota_fiscal=normalizar_str(item.nota_fiscal),
        numero_serie=numero_serie_normalizado,
        regiao=regiao_final,
        status=status_resolvido
    )

    db.add(novo_ativo)
    db.commit()
    db.refresh(novo_ativo)
    return novo_ativo


# =========================================================
# LISTAR ATIVOS
# =========================================================
@router.get("/", response_model=List[AtivoResponse])
def listar_ativos(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if getattr(user, "regiao", None):
        return db.query(Ativo).filter(Ativo.regiao == user.regiao).all()

    return db.query(Ativo).all()


# =========================================================
# ATUALIZAR ATIVO POR ID
# =========================================================
@router.put("/{ativo_id}", response_model=AtivoResponse)
def atualizar_ativo(
    ativo_id: int,
    dados: AtivoUpdate,
    db: Session = Depends(get_db)
):
    ativo = db.query(Ativo).filter(Ativo.id == ativo_id).first()

    if not ativo:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")

    for campo, valor in dados.dict(exclude_unset=True).items():
        setattr(ativo, campo, valor)

    db.commit()
    db.refresh(ativo)
    return ativo


# =========================================================
# DELETAR ATIVO
# =========================================================
@router.delete("/{ativo_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_ativo(
    ativo_id: int,
    db: Session = Depends(get_db)
):
    ativo = db.query(Ativo).filter(Ativo.id == ativo_id).first()

    if not ativo:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")

    db.delete(ativo)
    db.commit()
