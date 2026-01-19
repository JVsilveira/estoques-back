from pydantic import BaseModel
from typing import Optional
from enum import Enum


class StatusItem(str, Enum):
    em_estoque = "em_estoque"
    em_uso = "em_uso"


# =========================================================
# BASE (NÃO expõe status)
# =========================================================
class AtivoBase(BaseModel):
    tipo_item: str
    marca: str
    modelo: str
    numero_serie: str
    nota_fiscal: Optional[str] = None


# =========================================================
# CREATE → recebe CONTEXTO
# =========================================================

class AtivoCreate(BaseModel):
    tipo_item: str
    marca: Optional[str]
    modelo: Optional[str]
    nota_fiscal: Optional[str]
    numero_serie: str
    contexto: str
    regiao: Optional[str] 


# =========================================================
# UPDATE MANUAL (status permitido aqui, se quiser)
# =========================================================
class AtivoUpdate(BaseModel):
    tipo_item: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    nota_fiscal: Optional[str] = None
    status: Optional[StatusItem] = None


# =========================================================
# RESPONSE → expõe status
# =========================================================
class AtivoResponse(AtivoBase):
    id: int
    regiao: str
    status: StatusItem

    class Config:
        from_attributes = True
