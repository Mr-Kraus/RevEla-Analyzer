from pydantic import BaseModel
from typing import Any, Optional, Generic, TypeVar

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    """
    Fase M04.2: Contrato Padrão da API.
    Nenhum endpoint deve retornar dados fora deste envelopamento.
    """
    success: bool
    data: Optional[T] = None
    message: str = ""