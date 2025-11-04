from pydantic import BaseModel

class UserBase(BaseModel):
    nome: str
    matricula: str
    cargo: str | None = None
    regiao: str | None = None
    tipo_usuario: str | None = "comum"

class UserCreate(UserBase):
    senha: str

class UserUpdate(BaseModel):
    nome: str | None = None
    cargo: str | None = None
    regiao: str | None = None
    tipo_usuario: str | None = None
    senha: str | None = None

class UserResponse(UserBase):
    id: int

class Config:
    from_attributes = True