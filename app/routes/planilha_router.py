from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.dependencies import get_db
from app.core.auth import get_current_user
from app import models

router = APIRouter(prefix="/planilhas", tags=["Planilhas"])

@router.get("/ativos")
def listar_ativos(
    regiao: Optional[str] = Query(None, description="Filtro opcional de região (apenas para admin)"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Retorna os ativos de acordo com o perfil do usuário:
    - Usuário comum → apenas os ativos da sua região.
    - Admin → pode ver todos ou filtrar por uma região específica.
    """
    
    if current_user.role == "admin":
        if regiao:
            ativos = db.query(models.Ativo).filter(models.Ativo.regiao == regiao).all()
        else:
            ativos = db.query(models.Ativo).all()

    else:
        if not current_user.region:
            raise HTTPException(status_code=400, detail="Usuário sem região definida.")
        ativos = db.query(models.Ativo).filter(models.Ativo.regiao == current_user.region).all()

    return ativos
