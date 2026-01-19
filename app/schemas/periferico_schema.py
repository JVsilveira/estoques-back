from pydantic import BaseModel
from typing import Optional
from enum import Enum


class ContextoMovimentacao(str, Enum):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"


class PerifericoBase(BaseModel):
    tipo_item: str
    quantidade: int


class PerifericoCreate(PerifericoBase):
    contexto: ContextoMovimentacao


class PerifericoUpdate(BaseModel):
    tipo_item: Optional[str] = None
    quantidade: Optional[int] = None


class PerifericoResponse(PerifericoBase):
    id: int
    regiao: str

    class Config:
        from_attributes = True
