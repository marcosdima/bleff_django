from typing import Any
from django.forms import ValidationError
from django.db.models import Model
from django.utils.deconstruct import deconstructible

@deconstructible
class FieldNull:
    '''
        Raise a ValidationError if model.field is null. 'should_be' allows to change the functionality, if it is False then expects the field to be non-null.
    '''

    def __init__(self, field: str, should_be: bool = True) -> None:
        self.field = field
        self.should_be = should_be

    
    def __call__(self, model) -> Any:
        attribute_is_null = hasattr(model, self.field) and getattr(model, self.field)

        if not attribute_is_null and self.should_be:
            raise ValidationError(f'Expects {self.field} to be null')
        elif attribute_is_null and not self.should_be:
            raise ValidationError(f'Expects {self.field} to be non-null')

