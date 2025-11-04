from fastapi import FastAPI, Depends
from app.core.config import settings
from app.core.database import SessionLocal
import app.routes.ativo_router as ativos_router
import app.routes.periferico_router as perifericos_router
import app.routes.user_router as user_router
import app.routes.planilha_router as planilha_router
import app.routes.entrada_router as entrada_router
import app.routes.saida_router as saida_router
import app.routes.estoque_router as estoque_router

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

app.include_router(ativos_router.router)
app.include_router(perifericos_router.router)
app.include_router(user_router.router)
app.include_router(planilha_router.router)
app.include_router(entrada_router.router)
app.include_router(saida_router.router)
app.include_router(estoque_router.router)