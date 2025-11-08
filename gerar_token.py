import jwt
from app.core.config import settings
from app.core.auth import create_access_token

# Cria token com sub como string
token = create_access_token({"sub": "1", "role": "administrador", "regiao": None})
print("Token gerado:", token)

# Decodifica
payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
print("Payload:", payload)
