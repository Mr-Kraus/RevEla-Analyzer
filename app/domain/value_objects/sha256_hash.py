import re
from app.domain.exceptions.base_exceptions import ValidationError

class Sha256Hash:
    """Value Object para representar e validar um hash SHA-256."""
    
    def __init__(self, value: str):
        if not value:
            raise ValidationError("O hash SHA-256 não pode ser vazio.")
            
        value = value.strip().lower()
        if not re.fullmatch(r"^[a-f0-9]{64}$", value):
            raise ValidationError("O hash SHA-256 deve conter exatamente 64 caracteres hexadecimais.")
            
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Sha256Hash):
            return self.value == other.value
        return False

    def __str__(self) -> str:
        return self.value