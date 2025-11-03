from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    registration_number: str
    email: EmailStr
    role: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str]
    registration_number: Optional[str]
    email: Optional[EmailStr]
    role: Optional[str]
    password: Optional[str]

class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True