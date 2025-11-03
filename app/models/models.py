from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


# -----------------------------
# ENUMS
# -----------------------------
class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


# -----------------------------
# SQLALCHEMY MODELS
# -----------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    registration_number = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default=UserRole.USER.value)
    region = Column(String, nullable=True)  # estoque vinculado (user) ou None (admin)

    # Relacionamento com ativos alocados
    assigned_assets = relationship("AssetStock", back_populates="assigned_to")


class PeripheralStock(Base):
    __tablename__ = "peripheral_stock"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)       # ex: Teclado com fio
    quantity = Column(Integer, default=0)
    region = Column(String, nullable=False)     # região do estoque


class AssetStock(Base):
    __tablename__ = "asset_stock"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)       # notebook, monitor, desktop...
    serial_number = Column(String, unique=True, nullable=False)
    model = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    invoice_number = Column(String, nullable=True)  # nota fiscal
    available = Column(Boolean, default=True)       # em estoque ou alocado
    region = Column(String, nullable=False)        # região do estoque

    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_to = relationship("User", back_populates="assigned_assets")


# -----------------------------
# PYDANTIC SCHEMAS
# -----------------------------
class UserBase(BaseModel):
    username: str
    registration_number: str
    email: EmailStr
    role: str
    region: Optional[str]


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str]
    registration_number: Optional[str]
    email: Optional[EmailStr]
    role: Optional[str]
    region: Optional[str]
    password: Optional[str]


class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True