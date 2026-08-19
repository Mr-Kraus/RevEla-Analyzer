from fastapi import Depends, HTTPException, status
from typing import List
from app.infrastructure.database.models.security_model import UserModel
from app.api.dependencies.auth_dependency import get_current_user

class RequirePermission:
    """
    Dependência do FastAPI para fiscalizar permissões (RBAC).
    Pode ser injetada em qualquer rota.
    """
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    def __call__(self, current_user: UserModel = Depends(get_current_user)):
        # Admin Supremo: se o usuário tiver o Role 'Administrator', pula a checagem
        for role in current_user.roles:
            if role.name == "Administrator":
                return True
            
            # Checa se o usuário possui a permissão específica em alguma de suas roles
            for permission in role.permissions:
                if permission.code == self.required_permission:
                    return True

        # Se rodou todo o loop e não encontrou, barra o acesso
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acesso negado. Requer permissão: {self.required_permission}"
        )