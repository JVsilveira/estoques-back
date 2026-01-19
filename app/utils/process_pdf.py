import re
from app.utils.extract_text import extract_text_from_pdf
from app.utils.extract_con import extract_concessao_data
from app.utils.extract_dev import extract_devolucao_data


PAT_CON = re.compile(r"(termo\s*de\s*concess(?:a|ã)o|entrego\s*para\s*uso)", re.I)
PAT_DEV = re.compile(r"(termo\s*de\s*devolu(?:c|ç)(?:a|ã)o|devolu(?:c|ç)(?:a|ã)o\s*de\s*equipamento)", re.I)
PAT_RAT = re.compile(r"relatorio de ativacao tecnica", re.I)

def process_pdf(path: str, contexto: str) -> list:

    contexto = contexto.upper()

    texto = extract_text_from_pdf(path)
    texto_lower = texto.lower()

    registros = []

    # ---------- ENTRADA ----------
    if contexto == "ENTRADA":
        m_dev = PAT_DEV.search(texto_lower)
        if not m_dev:
            return []

        registro = extract_devolucao_data(texto[m_dev.start():])
        registro["TERMO"] = "DEVOLUÇÃO"
        registros.append(registro)
        
    # ---------- SAÍDA ----------
    elif contexto == "SAIDA":
        m_con = PAT_CON.search(texto_lower)
        if not m_con:
            return []

        registro = extract_concessao_data(texto[m_con.start():])
        registro["TERMO"] = "CONCESSÃO"
        registros.append(registro)

    return registros