from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from app.core.dependencies import get_db
from app.core.auth import get_current_user
from app import models

router = APIRouter(prefix="/estoque", tags=["Estoque"])


@router.get("/", response_model=dict)
def listar_estoque(
    regiao: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Retorna a contagem resumida do estoque de periféricos e ativos.
    - Usuário comum vê apenas sua própria região.
    - Admin pode ver todas ou filtrar com ?regiao=SP.
    """

    # 🔐 Se o usuário não for admin, força o filtro pela sua região
    if current_user.role != "admin":
        regiao = current_user.regiao
        if not regiao:
            raise HTTPException(status_code=400, detail="Usuário sem região definida.")

    # ------------------------------
    # 🖱️ 1️⃣ Contagem de periféricos
    # ------------------------------
    perifericos_query = db.query(
        models.Periferico.tipo.label("item"),
        func.sum(models.Periferico.quantidade).label("quantidade")
    )

    if regiao:
        perifericos_query = perifericos_query.filter(models.Periferico.regiao == regiao)

    perifericos_query = perifericos_query.group_by(models.Periferico.tipo).all()

    perifericos = [
        {"item": p.item, "quantidade": int(p.quantidade)} for p in perifericos_query
    ]

    # ------------------------------
    # 💻 2️⃣ Contagem de ativos
    # ------------------------------
    ativos_query = db.query(
        models.Ativo.modelo.label("item"),
        func.count(models.Ativo.id).label("quantidade")
    )

    if regiao:
        ativos_query = ativos_query.filter(models.Ativo.regiao == regiao)

    ativos_query = ativos_query.group_by(models.Ativo.modelo).all()

    ativos = [
        {"item": a.item, "quantidade": int(a.quantidade)} for a in ativos_query
    ]

    # ------------------------------
    # 🔁 3️⃣ Retorno combinado
    # ------------------------------
    return {
        "perifericos": perifericos,
        "ativos": ativos,
        "regiao": regiao if regiao else "Todas"
    }
