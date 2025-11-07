from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.models.user_model import User
from app.models.ativo_model import Ativo
from app.core.dependencies import get_current_user, get_db

router = APIRouter(prefix="/planilhas", tags=["Planilhas"])

@router.get("/ativos")
def listar_ativos(
    regiao: Optional[str] = Query(None, description="Filtro opcional de região (apenas para admin)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna os ativos de acordo com o perfil do usuário:
    - Usuário comum → apenas os ativos da sua região.
    - Admin → pode ver todos ou filtrar por uma região específica.
    """

    # Usuário administrador
    if current_user.role.lower() == "administrador":
        if regiao and regiao.strip():  # filtra por região se fornecida
            ativos = db.query(Ativo).filter(Ativo.regiao == regiao).all()
        else:
            ativos = db.query(Ativo).all()
    # Usuário comum
    else:
        if not current_user.regiao:
            raise HTTPException(
                status_code=400,
                detail="Usuário sem região definida. Contate o administrador."
            )
        ativos = db.query(Ativo).filter(Ativo.regiao == current_user.regiao).all()

    return ativos
