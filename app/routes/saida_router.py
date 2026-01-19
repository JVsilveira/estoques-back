from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
from app.core.dependencies import get_db, get_current_user
from app.models.ativo_model import Ativo, StatusItem as StatusAtivo
from app.models.periferico_model import Periferico, StatusItem as StatusPeriferico

router = APIRouter(prefix="/saida", tags=["Movimentação de Estoque"])

@router.post("/")
def registrar_saida(dados: Dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    print("🔥 ENDPOINT DE SAÍDA CHAMADO 🔥")
    regiao = dados.get("regiao") or getattr(user, "regiao", None)
    if not regiao:
        raise HTTPException(status_code=400, detail="Região não especificada.")

    ativos_atualizados = []
    perifericos_atualizados = []
    erros = []

    try:
        # ------------------------
        # ATIVOS
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

            if not ativo_db:
                erros.append({"item": ativo, "erro": "Ativo não encontrado no banco"})
                continue

            ativo_db.status = StatusAtivo.EM_USO
            ativos_atualizados.append(ativo_db.numero_serie)

        # ------------------------
        # PERIFÉRICOS
        # ------------------------
        for perif in dados.get("perifericos", []):
            tipo = perif.get("tipo_item")
            qtd = perif.get("quantidade", 1)

            if not tipo:
                erros.append({"item": perif, "erro": "Tipo não especificado"})
                continue

            perif_db = db.query(Periferico).filter(
                Periferico.tipo_item == tipo,
                Periferico.regiao == regiao
            ).first()

            if not perif_db:
                erros.append({"item": perif, "erro": "Periférico não encontrado"})
                continue

            if perif_db.quantidade < qtd:
                erros.append({
                    "item": tipo,
                    "erro": f"Quantidade insuficiente ({perif_db.quantidade} disponíveis)"
                })
                continue

            perif_db.quantidade -= qtd

            if perif_db.quantidade == 0:
                perif_db.status = StatusPeriferico.EM_USO

            perifericos_atualizados.append({
                "tipo_item": tipo,
                "quantidade_restante": perif_db.quantidade
            })

        # ✅ UM ÚNICO COMMIT
        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "mensagem": "Saída processada com sucesso.",
        "regiao": regiao,
        "ativos_atualizados": ativos_atualizados,
        "perifericos_atualizados": perifericos_atualizados,
        "erros": erros
    }
