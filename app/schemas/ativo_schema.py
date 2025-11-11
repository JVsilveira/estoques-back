from pydantic import BaseModel
from typing import Optional
from enum import Enum

class StatusItem(str, Enum):
    em_estoque = "em_estoque"
    em_uso = "em_uso"

class AtivoBase(BaseModel):
    tipo_item: str
    marca: str
    modelo: str
    nota_fiscal: Optional[str] = None
    numero_serie: str
    status: Optional[StatusItem] = StatusItem.em_estoque

class AtivoCreate(AtivoBase):
    pass

class AtivoUpdate(AtivoBase):
    pass

class AtivoResponse(AtivoBase):
    id: int
    regiao: str

class Config:
    from_attributes = True
