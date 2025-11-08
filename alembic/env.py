import sys
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# ---------------------------
# Caminho da raiz do projeto
# ---------------------------
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Carrega variáveis do .env
load_dotenv(dotenv_path=os.path.join(sys.path[0], ".env"))

# ---------------------------
# Importa sua configuração e modelos
# ---------------------------
from app.core.config import settings
from app.core.database import Base
from app.models import User, Ativo, Periferico  # todos os modelos

# ---------------------------
# Configuração do Alembic
# ---------------------------
config = context.config

# Configura o log
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# URL do banco de dados (do .env)
database_url = getattr(settings, "database_url", None)
if not database_url:
    raise ValueError("settings.database_url não definido")

config.set_main_option("sqlalchemy.url", database_url)

# Metadados para autogenerate
target_metadata = Base.metadata

# ---------------------------
# Modo offline
# ---------------------------
def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

# ---------------------------
# Modo online
# ---------------------------
def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

# ---------------------------
# Executa migração
# ---------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
