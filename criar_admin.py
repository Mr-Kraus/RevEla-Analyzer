import bcrypt
from app.infrastructure.database.models.security_model import UserModel
from app.infrastructure.database.session.database import SessionLocal 

def get_password_hash(password: str) -> str:
    # Transforma a string em bytes, gera o sal e depois faz o hash
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode('utf-8') # Converte de volta pra string pra salvar no banco

def setup_admin_user():
    db = SessionLocal() 
    
    try:
        email_teste = "admin@revela.com"
        senha_teste = "senha123"
        
        user = db.query(UserModel).filter(UserModel.email == email_teste).first()
        
        if user:
            user.password_hash = get_password_hash(senha_teste)
            print(f"Senha do usuário {email_teste} atualizada para '{senha_teste}'.")
        else:
            new_user = UserModel(
                name="Administrador Local",
                email=email_teste,
                password_hash=get_password_hash(senha_teste),
                is_active=True
            )
            db.add(new_user)
            print(f"Usuário {email_teste} criado com sucesso!")
            
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Erro ao criar usuário: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    setup_admin_user()