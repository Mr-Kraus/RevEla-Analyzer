from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import uuid
from pydantic import BaseModel

from app.api.dependencies.db_dependency import get_db
from app.api.schemas.base_schema import APIResponse
from app.application.services.auth_service import AuthService
from app.api.dependencies.auth_dependency import get_current_user
from app.infrastructure.database.models.security_model import UserModel


router = APIRouter(prefix="/auth", tags=["Authentication"])

# 1. ROTA DE LOGIN ADAPTADA PARA O SWAGGER
@router.post("/login")
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Recebe credenciais via formulário OAuth2 e devolve o Token JWT diretamente."""
    auth_service = AuthService(db)
    
    try:
        # O Swagger sempre envia o campo 'username', mas nós usamos ele para receber o 'email'
        access_token = auth_service.authenticate_user(request.username, request.password)
        
        # O Swagger PRECISA que o retorno seja plano, sem o APIResponse aqui!
        return {"access_token": access_token, "token_type": "bearer"}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

# 2. DTO DE RESPOSTA DO USUÁRIO
class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    is_active: bool

# 3. ROTA PROTEGIDA DE TESTE
@router.get("/me", response_model=APIResponse[UserResponse])
def get_me(current_user: UserModel = Depends(get_current_user)):
    """Retorna os dados do usuário atualmente logado (exige Token)."""
    user_data = UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        is_active=current_user.is_active
    )
    return APIResponse(success=True, data=user_data, message="Dados recuperados com sucesso.")