from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    app_name: str = "Estoques API"  # valor padrão

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }

settings = Settings()