from sqlalchemy.orm import Session
from sqlalchemy import select
from app.infrastructure.database.models.security_model import UserModel
from app.api.security.password import verify_password
from app.api.security.jwt import create_access_token

class AuthService:
    def __init__(self, session: Session):
        self.session = session

    def authenticate_user(self, email: str, password: str) -> str:
        """Verifica as credenciais e retorna o token de acesso (JWT)."""
        stmt = select(UserModel).where(UserModel.email == email)
        user = self.session.execute(stmt).scalar_one_or_none()

        if not user:
            raise ValueError("E-mail ou senha incorretos.")
            
        if not user.is_active:
            raise ValueError("Usuário inativo. Contate o administrador.")

        if not verify_password(password, user.password_hash):
            raise ValueError("E-mail ou senha incorretos.")

        # Monta os dados que vão dentro do crachá (Payload)
        token_data = {"sub": str(user.id), "email": user.email}
        access_token = create_access_token(data=token_data)
        
        return access_token