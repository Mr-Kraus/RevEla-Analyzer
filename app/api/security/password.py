import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto plano bate com o hash seguro do banco."""
    # O bcrypt exige que as strings sejam convertidas para bytes (utf-8) antes da checagem
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Gera um hash seguro a partir de uma senha em texto plano."""
    # Gera um "sal" aleatório para a senha e cria o hash
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    # Retorna como string para podermos salvar no banco de dados (VARCHAR)
    return hashed_bytes.decode('utf-8')