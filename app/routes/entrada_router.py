from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
from app.core.dependencies import get_db, get_current_user
from app.models.ativo_model import Ativo, StatusItem as StatusAtivo
from app.models.periferico_model import Periferico, StatusItem as StatusPeriferico

router = APIRouter(prefix="/entrada", tags=["Movimentação de Estoque"])

@router.post("/")
def registrar_entrada(dados: Dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    regiao = dados.get("regiao") or getattr(user, "regiao", None)
    if not regiao:
        raise HTTPException(status_code=400, detail="Região não especificada.")

    ativos_processados = []
    perifericos_processados = []
    erros = []

    # ------------------------
    # PROCESSA ATIVOS
    # ------------------------
    for ativo in dados.get("ativos", []):
        numero_serie = ativo.get("numero_serie")

        if not numero_serie:
            erros.append({"item": ativo, "erro": "Ativo sem número de série"})
            continue

        ativo_db = db.query(Ativo).filter(
            Ativo.numero_serie == numero_serie,
            Ativo.regiao == regiao
        ).first()

        if ativo_db:
            # Atualiza status para 'em_estoque'
            ativo_db.status = StatusAtivo.EM_ESTOQUE
            db.commit()
            db.refresh(ativo_db)
            ativos_processados.append({"numero_serie": numero_serie, "acao": "atualizado"})
        else:
            # Cria novo ativo
            novo_ativo = Ativo(
                tipo_item=ativo.get("tipo_item"),
                marca=ativo.get("marca"),
                modelo=ativo.get("modelo"),
                nota_fiscal=ativo.get("nota_fiscal"),
                numero_serie=numero_serie,
                regiao=regiao,
                status=StatusAtivo.EM_ESTOQUE
            )
            db.add(novo_ativo)
            db.commit()
            db.refresh(novo_ativo)
            ativos_processados.append({"numero_serie": numero_serie, "acao": "criado"})

    # ------------------------
    # PROCESSA PERIFÉRICOS
    # ------------------------
    for perif in dados.get("perifericos", []):
        tipo = perif.get("tipo_item")
        qtd = perif.get("quantidade", 1)

        if not tipo:
            erros.append({"item": perif, "erro": "Tipo de periférico não especificado"})
            continue

        perif_db = db.query(Periferico).filter(
            Periferico.tipo_item == tipo,
            Periferico.regiao == regiao
        ).first()

        if perif_db:
            # ✅ Soma a quantidade existente
            perif_db.quantidade += qtd
            perif_db.status = StatusPeriferico.EM_ESTOQUE
            db.commit()
            db.refresh(perif_db)
            perifericos_processados.append({
                "tipo_item": tipo,
                "acao": f"quantidade_atualizada (+{qtd})",
                "quantidade_total": perif_db.quantidade
            })
