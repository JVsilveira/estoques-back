from sqlalchemy import Column, Integer, String, Enum
from app.core.database import Base
import enum

class StatusItem(enum.Enum):
    EM_ESTOQUE = "em_estoque"
    EM_USO = "em_uso"

class Ativo(Base):
    __tablename__ = "ativos"

    id = Column(Integer, primary_key=True, index=True)
    tipo_item = Column(String, nullable=False)      
    marca = Column(String, nullable=False)
    modelo = Column(String, nullable=False)
    nota_fiscal = Column(String, nullable=True)
    numero_serie = Column(String, nullable=False, unique=True)
    status = Column(
    Enum(StatusItem, native_enum=False),
    nullable=False,
    default=StatusItem.EM_ESTOQUE
)
    regiao = Column(String, nullable=False)
