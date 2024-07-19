from typing import Any
from django.forms import ValidationError
from django.db.models import Model
from django.utils.deconstruct import deconstructible

@deconstructible
class FieldNull:
    '''
        Raise a ValidationError if model.field is null. 'should_be' allows to change the functionality, if it is False then expects the field to be non-null.
    '''

    def __init__(self, model: Model, field: str, should_be: bool = True) -> None:
        self.field = field
        self.should_be = should_be
        self.model = model
    
    def __call__(self, model_id) -> Any:
        model = self.model.objects.get(id=model_id)

        if not hasattr(model, self.field):
            raise ValidationError(f"Expects '{self.field}' to be part of {model._meta.model_name}")

        attribute_is_null = getattr(model, self.field)

        if attribute_is_null and self.should_be:
            raise ValidationError(f'Expects {model._meta.model_name}.{self.field} to be null')
        elif attribute_is_null and not self.should_be:
            raise ValidationError(f'Expects {model._meta.model_name}.{self.field} to be non-null')
