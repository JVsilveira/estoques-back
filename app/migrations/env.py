import sys
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# 🧠 Adiciona o caminho da raiz do projeto ao sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Agora sim podemos importar módulos da app
from app.core.config import settings
from app.core.database import Base  # ⚠️ confirme se o seu arquivo se chama database.py ou core/database.py
from app.models import User, Ativo, Periferico

# Este objeto é fornecido pelo Alembic
config = context.config

# Configura o arquivo de log (alembic.ini)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Define a URL do banco de dados a partir do settings (.env)
config.set_main_option("sqlalchemy.url", settings.database_url)

# Metadados dos modelos
target_metadata = Base.metadata


def run_migrations_offline():
    """Executa as migrações no modo 'offline'."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Executa as migrações no modo 'online'."""
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


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
