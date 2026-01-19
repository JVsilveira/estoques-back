from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
from app.core.dependencies import get_db, get_current_user
from app.models.ativo_model import Ativo, StatusItem as StatusAtivo
from app.models.periferico_model import Periferico

router = APIRouter(prefix="/entrada", tags=["Movimentação de Estoque"])


@router.post("/")
def registrar_entrada(
    dados: Dict,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # ========================
    # RESOLUÇÃO DE REGIÃO
    # ========================
    regiao_payload = dados.get("regiao")
    regiao_token = getattr(user, "regiao", None)

    if regiao_token:
        # usuário comum
        if regiao_payload and regiao_payload != regiao_token:
            raise HTTPException(
                status_code=403,
                detail="Usuário não pode operar em outra região."
            )
        regiao = regiao_token
    else:
        # administrador
        if not regiao_payload:
            raise HTTPException(
                status_code=400,
                detail="Administrador deve informar a região no payload."
            )
        regiao = regiao_payload

    # ========================
    # CONTEXTO (DEFAULT)
    # ========================
    contexto = dados.get("contexto", "ENTRADA").upper()
    if contexto not in ["ENTRADA", "SAIDA"]:
        raise HTTPException(
            status_code=400,
            detail="Contexto inválido. Use ENTRADA ou SAIDA."
        )

    ativos_processados = []
    perifericos_processados = []
    erros = []

    # ========================
    # PROCESSA ATIVOS
    # ========================
    for ativo in dados.get("ativos", []):
        numero_serie = ativo.get("numero_serie")
        if not numero_serie:
            erros.append({"item": ativo, "erro": "Ativo sem número de série"})
            continue

        try:
            ativo_db = db.query(Ativo).filter(
                Ativo.numero_serie == numero_serie,
                Ativo.regiao == regiao
            ).first()

            novo_status = (
                StatusAtivo.EM_ESTOQUE
                if contexto == "ENTRADA"
                else StatusAtivo.EM_USO
            )

            if ativo_db:
                ativo_db.status = novo_status
                ativos_processados.append({
                    "numero_serie": numero_serie,
                    "acao": "atualizado",
                    "status": novo_status.value
                })
            else:
                novo_ativo = Ativo(
                    tipo_item=ativo.get("tipo_item", "NOTEBOOK"),
                    marca=ativo.get("marca", "----------"),
                    modelo=ativo.get("modelo", "----------"),
                    nota_fiscal=ativo.get("nota_fiscal"),
                    numero_serie=numero_serie,
                    regiao=regiao,
                    status=novo_status
                )
                db.add(novo_ativo)
                ativos_processados.append({
                    "numero_serie": numero_serie,
                    "acao": "criado",
                    "status": novo_status.value
                })

        except Exception as e:
            erros.append({"item": ativo, "erro": str(e)})

    # ========================
    # PROCESSA PERIFÉRICOS
    # ========================
    for perif in dados.get("perifericos", []):
        tipo = perif.get("tipo_item")
        qtd = perif.get("quantidade", 1)

        if not tipo:
            erros.append({"item": perif, "erro": "Periférico sem tipo"})
            continue

        try:
            perif_db = db.query(Periferico).filter(
                Periferico.tipo_item == tipo,
                Periferico.regiao == regiao
            ).first()

            if perif_db:
                perif_db.quantidade += qtd
                perifericos_processados.append({
                    "tipo_item": tipo,
                    "acao": "quantidade_atualizada",
                    "quantidade_total": perif_db.quantidade
                })
            else:
                novo_perif = Periferico(
                    tipo_item=tipo,
                    quantidade=qtd,
                    regiao=regiao
                )
                db.add(novo_perif)
                perifericos_processados.append({
                    "tipo_item": tipo,
                    "acao": "criado",
                    "quantidade_total": qtd
                })

        except Exception as e:
            erros.append({"item": perif, "erro": str(e)})

    # ========================
    # VALIDA SE PROCESSOU ALGO
    # ========================
    if not ativos_processados and not perifericos_processados:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Nenhum item válido para processar."
        )

    # ========================
    # COMMIT FINAL
    # ========================
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao salvar no banco: {str(e)}"
        )

    return {
        "regiao": regiao,
        "contexto": contexto,
        "ativos_processados": ativos_processados,
        "perifericos_processados": perifericos_processados,
        "erros": erros
    }
