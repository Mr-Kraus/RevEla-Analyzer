from app.infrastructure.database.session.database import SessionLocal
from app.infrastructure.database.models.security_model import UserModel
from app.api.security.password import get_password_hash

db = SessionLocal()

admin_user = UserModel(
    name="Administrador",
    email="admin@revela.com",
    password_hash=get_password_hash("senha123"), # Senha criptografada na hora!
    is_active=True
)

db.add(admin_user)
db.commit()
print("Usuário Admin criado com sucesso!")
db.close()