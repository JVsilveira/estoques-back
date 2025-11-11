from pydantic import BaseModel
from typing import Optional
from enum import Enum

class StatusItem(str, Enum):
    em_estoque = "em_estoque"
    em_uso = "em_uso"
    baixado = "baixado"

class PerifericoBase(BaseModel):
    tipo_item: str
    quantidade: Optional[int] = 0
    status: Optional[StatusItem] = StatusItem.em_estoque

class PerifericoCreate(PerifericoBase):
    pass

class PerifericoUpdate(PerifericoBase):
    pass

class PerifericoResponse(PerifericoBase):
    id: int
    regiao: str

class Config:
    from_attributes = True
