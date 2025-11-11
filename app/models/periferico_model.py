from sqlalchemy import Column, Integer, String, Enum
from app.core.database import Base
import enum

class StatusItem(enum.Enum):
    EM_ESTOQUE = "em_estoque"
    EM_USO = "em_uso"

class Periferico(Base):
    __tablename__ = "perifericos"

    id = Column(Integer, primary_key=True, index=True)
    tipo_item = Column(String)
    quantidade = Column(Integer)
    regiao = Column(String)
