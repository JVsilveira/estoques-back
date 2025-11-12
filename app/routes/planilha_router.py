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
    print("Usuário autenticado:", current_user.matricula, current_user.role, current_user.regiao)
    print("Região solicitada:", regiao)

    # Usuário administrador
    if current_user.role.lower() == "administrador":
        if regiao and regiao.strip() and regiao.upper() != "TODAS":
            ativos = db.query(Ativo).filter(Ativo.regiao == regiao).all()
        else:
            ativos = db.query(Ativo).all()
    else:
        if not current_user.regiao:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuário sem região definida. Contate o administrador."
            )
        ativos = db.query(Ativo).filter(Ativo.regiao == current_user.regiao).all()

    print("Qtd de ativos retornados:", len(ativos))

    # Se a lista estiver vazia, devolve array vazio (não None)
    if not ativos:
        return []

    resposta = [
        {
            "tipo": a.tipo_item,
            "numero_serie": a.numero_serie,
            "modelo": a.modelo,
            "marca": a.marca,
            "numero_ativo": a.nota_fiscal,
            "status": "Em estoque" if a.status.value == "em_estoque" else "Em uso",
            "regiao": a.regiao
        }
        for a in ativos
    ]

    print("Exemplo de resposta:", resposta[0] if resposta else "lista vazia")
    return resposta

