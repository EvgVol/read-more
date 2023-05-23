class RequiredFieldsMixin:
    """Осуществляет проверку на заполнение всех обязательных полей."""

    def clean(self):
        cleaned_data = super().clean()

        for field_name in self.fields:
            if not cleaned_data.get(field_name):
                self.add_error(
                    field_name,
                    f'{self.fields[field_name].label} обязательно для заполнения')
        return cleaned_data