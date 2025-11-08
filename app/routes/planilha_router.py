from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.models.user_model import User
from app.models.ativo_model import Ativo
from app.core.dependencies import get_current_user, get_db

router = APIRouter(prefix="/planilhas", tags=["Planilhas"])

@router.get("/ativos")
def listar_ativos(
    regiao: Optional[str] = Query(None, description="Filtro opcional de região (apenas admin)"),
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
        if regiao and regiao.strip() and regiao.upper() != "TODAS":
            ativos = db.query(Ativo).filter(Ativo.regiao == regiao).all()
        else:
            ativos = db.query(Ativo).all()
    # Usuário comum
    else:
        if not current_user.regiao:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuário sem região definida. Contate o administrador."
            )
        ativos = db.query(Ativo).filter(Ativo.regiao == current_user.regiao).all()

    return [
        {
            "tipo": a.tipo,
            "numero_serie": a.numero_serie,
            "modelo": a.modelo,
            "marca": a.marca,
            "numero_ativo": a.numero_ativo,
            "status": a.status,
            "regiao": a.regiao
        }
        for a in ativos
    ]
