from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Classe base para todos os modelos SQLAlchemy.
    Nenhuma entidade de domínio deve herdar desta classe.
    """
    pass