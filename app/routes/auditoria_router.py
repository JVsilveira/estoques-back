from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from typing import List, Optional
import tempfile
import os

from app.core.dependencies import get_db, get_current_user
from app.utils.process_pdf import process_pdf
from app.utils.validar_termo import validar_termo

router = APIRouter(
    prefix="/auditoria",
    tags=["Auditoria"]
)

@router.post("/processar-pdfs")
async def processar_pdfs(
    contexto: str = Form(...),
    regiao: Optional[str] = Form(None),
    arquivos: List[UploadFile] = File(...),
    user=Depends(get_current_user)
):
    contexto = contexto.upper()

    if contexto not in ("ENTRADA", "SAIDA"):
        raise HTTPException(status_code=400, detail="Contexto inválido")

    # =====================================================
    # RESOLUÇÃO DEFINITIVA DA REGIÃO
    # =====================================================
    if regiao:
        regiao_final = regiao.upper()

    elif getattr(user, "regiao", None):
        regiao_final = user.regiao.upper()

    else:
        raise HTTPException(
            status_code=400,
            detail="Admin deve selecionar uma região"
        )

    termos_validos = []
    termos_invalidos = []

    for arquivo in arquivos:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await arquivo.read())
            caminho_pdf = tmp.name

        try:
            registros = process_pdf(caminho_pdf, contexto)

            if not registros:
                termos_invalidos.append({
                    "arquivo": arquivo.filename,
                    "erros": ["termo_nao_encontrado"],
                    "erros_descricao": [
                        f"Arquivo não contém termo de {'devolução' if contexto == 'ENTRADA' else 'concessão'}"
                    ]
                })
                continue

            for idx, registro in enumerate(registros):
                resultado_validacao = validar_termo(registro, contexto)

                if not resultado_validacao["valido"]:
                    termos_invalidos.append({
                        "arquivo": arquivo.filename,
                        "registro": idx,
                        "erros": resultado_validacao["erros"],
                        "erros_descricao": resultado_validacao["erros_descricao"]
                    })
                    continue

                ativos = []
                perifericos = []

                # ======================
                # ATIVO PRINCIPAL
                # ======================
                if registro.get("SERIAL"):
                    ativos.append({
                        "tipo_item": registro.get("TIPO_ATIVO") or registro.get("TIPO") or "NOTEBOOK",
                        "marca": registro.get("MARCA"),
                        "modelo": registro.get("MODELO"),
                        "nota_fiscal": registro.get("NF"),
                        "numero_serie": registro.get("SERIAL"),
                        "contexto": contexto,
                        "regiao": regiao_final
                    })

                # ======================
                # MONITOR
                # ======================
                if registro.get("SERIAL MONITOR") and registro.get("SERIAL MONITOR") != "----------":
                    ativos.append({
                        "tipo_item": "MONITOR",
                        "marca": registro.get("MARCA MONITOR"),
                        "modelo": registro.get("MODELO MONITOR"),
                        "nota_fiscal": registro.get("NF"),
                        "numero_serie": registro.get("SERIAL MONITOR"),
                        "contexto": contexto,
                        "regiao": regiao_final
                    })

                # ======================
                # PERIFÉRICOS (SEM STATUS)
                # ======================
                for item in [
                    "MOUSE", "HEADSET", "TECLADO", "WEBCAM", "DOCK STATION",
                    "CABO DE SEGURANÇA", "HUB USB", "CARREGADOR EXTRA",
                    "SUPORTE ERGONÔMICO", "MOCHILA", "BATERIA EXTRA",
                    "CABO RCA", "CABO DE FORÇA DO MONITOR"
                ]:
                    if registro.get(item) == "Sim":
                        perifericos.append({
                            "tipo_item": item,
                            "quantidade": 1,
                            "regiao": regiao_final
                        })

                termos_validos.append({
                    "arquivo": arquivo.filename,
                    "ativos": ativos,
                    "perifericos": perifericos
                })

        finally:
            os.remove(caminho_pdf)

    return {
        "contexto": contexto,
        "regiao": regiao_final,
        "quantidade_validos": len(termos_validos),
        "quantidade_invalidos": len(termos_invalidos),
        "termos_validos": termos_validos,
        "termos_invalidos": termos_invalidos
    }
