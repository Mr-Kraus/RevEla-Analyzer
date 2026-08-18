from app.domain.exceptions.base_exceptions import ValidationError

class DatasetCode:
    """Value Object para garantir a formatação de códigos do ReLeVa."""
    
    def __init__(self, value: str):
        if not value or not value.strip():
            raise ValidationError("O código de Dataset não pode ser vazio.")
            
        self._value = value.strip().upper()

    @property
    def value(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, DatasetCode):
            return self.value == other.value
        return False

    def __str__(self) -> str:
        return self.value