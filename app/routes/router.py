from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app import models, schemas
from app.core.database import get_db
from app.core.auth import (
    create_access_token,
    verify_password,
    get_password_hash,
    get_current_user,
)

router = APIRouter()


# -------------------------
# Schemas específicos para JSON
# -------------------------
class AccessoryItem(BaseModel):
    name: str
    quantidade: int


class AssetInput(BaseModel):
    assetNumber: str
    serialNumber: str
    tipo: str
    modelo: str
    marca: str
    nfNumber: Optional[str]
    disponibilidade: str  # "Em Uso" ou "Disponível"
    accessoriesCounted: List[AccessoryItem]
    region: Optional[str] = None  # opcional, só admin define


# -------------------------
# ROTAS DE LOGIN
# -------------------------
@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login do usuário:
    - Recebe username e password
    - Verifica credenciais com hash
    - Retorna token JWT contendo id, role e região
    """
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")

    # Gera token JWT com dados do usuário
    access_token = create_access_token(
        data={
            "sub": user.id,
            "username": user.username,
            "role": user.role,
            "region": user.region
        },
        expires_delta=timedelta(minutes=60)
    )

    return {"token": access_token, "token_type": "bearer"}


# -------------------------
# USERS CRUD
# -------------------------
@router.post("/users", response_model=schemas.UserOut)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Cria um novo usuário:
    - Apenas admin pode criar
    - A senha é automaticamente convertida em hash antes de salvar
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")

    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Usuário já existe")

    password_hash = get_password_hash(user.password)

    db_user = models.User(
        username=user.username,
        registration_number=user.registration_number,
        email=user.email,
        password_hash=password_hash,
        role=user.role,
        region=user.region
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.put("/users/me", response_model=schemas.UserOut)
def update_me(user_update: schemas.UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.put("/users/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


# -------------------------
# PERIPHERALS
# -------------------------
@router.get("/peripherals")
def list_peripherals(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    query = db.query(models.PeripheralStock)
    if current_user.role != "admin":
        query = query.filter(models.PeripheralStock.region == current_user.region)
    return query.all()


@router.post("/peripherals")
def create_peripheral(name: str, quantity: int, region: Optional[str] = None, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        region = current_user.region
    elif not region:
        raise HTTPException(status_code=400, detail="Região obrigatória para admin")

    db_peripheral = models.PeripheralStock(
        name=name,
        quantity=quantity,
        region=region
    )
    db.add(db_peripheral)
    db.commit()
    db.refresh(db_peripheral)
    return db_peripheral


@router.put("/peripherals/{peripheral_id}")
def update_peripheral(peripheral_id: int, quantity: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    peripheral = db.query(models.PeripheralStock).filter(models.PeripheralStock.id == peripheral_id).first()
    if not peripheral:
        raise HTTPException(status_code=404, detail="Periférico não encontrado")

    if current_user.role != "admin" and peripheral.region != current_user.region:
        raise HTTPException(status_code=403, detail="Acesso negado")

    peripheral.quantity = quantity
    db.commit()
    db.refresh(peripheral)
    return peripheral


# -------------------------
# ASSETS CRUD
# -------------------------
@router.get("/assets")
def list_assets(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    query = db.query(models.AssetStock)
    if current_user.role != "admin":
        query = query.filter(models.AssetStock.region == current_user.region)
    return query.all()


@router.put("/assets/{asset_id}")
def update_asset(asset_id: int, available: bool, assigned_to_id: Optional[int] = None, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    asset = db.query(models.AssetStock).filter(models.AssetStock.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")

    if current_user.role != "admin" and asset.region != current_user.region:
        raise HTTPException(status_code=403, detail="Acesso negado")

    asset.available = available
    asset.assigned_to_id = assigned_to_id
    db.commit()
    db.refresh(asset)
    return asset


# -------------------------
# Rota para receber JSON (ativo + acessórios)
# -------------------------
@router.post("/assets/json")
def create_or_update_asset(asset_data: AssetInput, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Define região
    if current_user.role == "admin" and asset_data.region:
        region = asset_data.region
    else:
        region = current_user.region

    if not region:
        raise HTTPException(status_code=400, detail="Região não definida")

    # Ativo principal
    db_asset = db.query(models.AssetStock).filter(models.AssetStock.serial_number == asset_data.serialNumber).first()
    available = asset_data.disponibilidade.lower() == "disponível"

    if db_asset:
        db_asset.type = asset_data.tipo.strip()
        db_asset.model = asset_data.modelo.strip()
        db_asset.brand = asset_data.marca.strip()
        db_asset.invoice_number = asset_data.nfNumber
        db_asset.available = available
        db_asset.region = region
    else:
        db_asset = models.AssetStock(
            type=asset_data.tipo.strip(),
            model=asset_data.modelo.strip(),
            brand=asset_data.marca.strip(),
            serial_number=asset_data.serialNumber,
            invoice_number=asset_data.nfNumber,
            available=available,
            region=region
        )
        db.add(db_asset)

    db.commit()
    db.refresh(db_asset)

    # Acessórios
    for accessory in asset_data.accessoriesCounted:
        db_peripheral = db.query(models.PeripheralStock).filter(
            models.PeripheralStock.name == accessory.name,
            models.PeripheralStock.region == region
        ).first()
        if db_peripheral:
            db_peripheral.quantity += accessory.quantidade
        else:
            db_peripheral = models.PeripheralStock(
                name=accessory.name,
                quantity=accessory.quantidade,
                region=region
            )
            db.add(db_peripheral)

    db.commit()
    return {"status": "success", "asset": db_asset}
