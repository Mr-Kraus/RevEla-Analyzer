from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Annotated
import jwt

from app.api.dependencies.db_dependency import get_db
from app.api.security.jwt import SECRET_KEY, ALGORITHM
from app.infrastructure.database.models.security_model import UserModel

# O FastAPI usa isso para extrair o token do cabeçalho automaticamente
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
) -> UserModel:
    """Extrai e valida o token JWT, retornando o usuário logado."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou token expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
    except jwt.PyJWTError: # Captura tokens inválidos ou expirados
        raise credentials_exception
        
    stmt = select(UserModel).where(UserModel.id == user_id_str)
    user = db.execute(stmt).scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Usuário inativo.")
        
    return user