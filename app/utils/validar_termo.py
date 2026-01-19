import re
from app.utils.validar_hostname import validar_hostname   

ERROS_DESCRICAO = {
    "nota_fiscal_invalida": "Nota fiscal ausente ou inválida",
    "termo_nao_assinado": "Termo não está assinado",
    "monitor_sem_serial": "Monitor informado sem número de série",
    "hostname_invalido": "Hostname fora do padrão",
    "chamado_ausente": "Chamado não informado",
    "chamado_invalido": "Número de chamado inválido"
}

PLACEHOLDER = re.compile(r"^-+$")

def validar_termo(dados: dict, contexto: str) -> dict:
    erros = []

    modelo = str(dados.get("MODELO", "")).strip().upper()
    nf = str(dados.get("NF", "")).strip()
    hostname = str(dados.get("HOSTNAME", "")).strip()
    matricula = str(dados.get("MATRICULA", "")).strip()

    # ---------------- ASSINATURA (sempre obrigatória) ----------------
    if not dados.get("ASSINADO", False):
        erros.append("termo_nao_assinado")

    # ---------------- NF ----------------
    if contexto == "SAIDA":
        nf = str(dados.get("NF", "")).strip()

    # remove zeros à esquerda
        nf_sem_zeros = nf.lstrip("0")

    # se ficar vazio ou tiver menos de 5 dígitos → inválido
        if not nf_sem_zeros or len(nf_sem_zeros) < 5:
            erros.append("nota_fiscal_invalida")

    # ---------------- HOSTNAME (somente SAÍDA) ----------------
    if contexto == "SAIDA":
        if (
            not hostname
            or PLACEHOLDER.fullmatch(hostname)
            or not validar_hostname(hostname, matricula if matricula else None)
        ):
            erros.append("hostname_invalido")

    # ---------------- CHAMADO (somente SAÍDA) ----------------
    if contexto == "SAIDA":
        chamado = str(dados.get("CHAMADO", "")).strip().upper()

        if not chamado:
            erros.append("chamado_ausente")
        elif chamado not in ["ROLLOUT", "ROLOUT"] and not re.match(r"^(REQ|INC)\d+$", chamado):
            erros.append("chamado_invalido")

    return {
        "valido": len(erros) == 0,
        "erros": erros,
        "erros_descricao": [ERROS_DESCRICAO[e] for e in erros]
    }
