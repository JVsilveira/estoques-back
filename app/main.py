from fastapi import FastAPI, Depends
from app.core.config import settings
from app.core.database import SessionLocal

app = FastAPI(
    title=settings.app_name
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "API de Estoques funcionando"}