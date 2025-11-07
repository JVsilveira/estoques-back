from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

import app.routes.ativo_router as ativos_router
import app.routes.periferico_router as perifericos_router
import app.routes.user_router as user_router
import app.routes.planilha_router as planilha_router
import app.routes.entrada_router as entrada_router
import app.routes.saida_router as saida_router
import app.routes.estoque_router as estoque_router
import app.routes.login_router as login_router

# -----------------------
# Cria a aplicação FastAPI
# -----------------------
app = FastAPI(
    title=settings.app_name
)

# -----------------------
# Configuração do CORS
# -----------------------
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,   # permite frontend React
    allow_credentials=True,
    allow_methods=["*"],     # GET, POST, PUT, DELETE, etc
    allow_headers=["*"],     # Authorization, Content-Type, etc
)

# -----------------------
# Rota raiz
# -----------------------
@app.get("/")
def read_root():
    return {"message": "API de Estoques funcionando"}

# -----------------------
# Inclui todos os routers
# -----------------------
app.include_router(ativos_router.router)
app.include_router(perifericos_router.router)
app.include_router(user_router.router)
app.include_router(planilha_router.router)
app.include_router(entrada_router.router)
app.include_router(saida_router.router)
app.include_router(estoque_router.router)
app.include_router(login_router.router)
