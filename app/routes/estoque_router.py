from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.models.user_model import User
from app.models.periferico_model import Periferico
from app.models.ativo_model import Ativo
from app.core.dependencies import get_current_user, get_db

router = APIRouter(prefix="/estoque", tags=["Estoque"])


@router.get("/", response_model=dict)
def listar_estoque(
    regiao: Optional[str] = Query(None, description="Filtro opcional de região (apenas admin)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna a contagem resumida do estoque de periféricos e ativos.
    - Usuário comum vê apenas sua própria região.
    - Admin pode ver todas ou filtrar com ?regiao=SP.
    """

    # 🔐 Se o usuário não for admin, força o filtro pela sua região
    if current_user.role.lower() == "administrador":
        filtro_regiao = regiao if regiao and regiao.upper() != "TODAS" else None
    else:
        if not current_user.regiao:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuário sem região definida. Contate o administrador."
            )
        filtro_regiao = current_user.regiao

    # ------------------------------
    # 🖱️ 1️⃣ Contagem de periféricos
    # ------------------------------
    perifericos_query = db.query(
        Periferico.tipo_item.label("item"),
        func.sum(Periferico.quantidade).label("quantidade")
    )

    if filtro_regiao:
        perifericos_query = perifericos_query.filter(Periferico.regiao == filtro_regiao)

    perifericos_query = perifericos_query.group_by(Periferico.tipo_item).all()

    perifericos = [
        {"item": p.item, "quantidade": int(p.quantidade)} for p in perifericos_query
    ]

    # ------------------------------
    # 💻 2️⃣ Contagem de ativos
    # ------------------------------
    ativos_query = db.query(
        Ativo.modelo.label("item"),
        func.count(Ativo.id).label("quantidade")
    )

    if filtro_regiao:
        ativos_query = ativos_query.filter(Ativo.regiao == filtro_regiao)

    ativos_query = ativos_query.group_by(Ativo.modelo).all()

    ativos = [
        {"item": a.item, "quantidade": int(a.quantidade)} for a in ativos_query
    ]

    # ------------------------------
    # 🔁 3️⃣ Retorno combinado
    # ------------------------------
    return {
        "perifericos": perifericos,
        "ativos": ativos,
        "regiao": filtro_regiao if filtro_regiao else "Todas"
    }
