from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class OrderField(models.PositiveIntegerField):
    """
    A Django model field for ordering objects.

    Allows objects to be ordered in a specific sequence. 
    When a model is created, `OrderField` automatically 
    assigns sequential numbers to each object.

    Args:
    for_fields (list): A list of fields used to group objects. 
        Must be unique for each object within a group.
    *args: Add'l arguments to pass to the superclass constructor.
    **kwargs: Add'l keyword arguments to pass to the superclass constructor.

    Attributes:
    requires_unique_target = True: A flag that indicates `OrderField` 
        should ensure the values of all records
    for the target model are unique.

    Usage:
    class MyModel(models.Model):
        order = OrderField(for_fields=['category'])
        name = models.CharField(max_length=255)
        category = models.ForeignKey(
            Category, on_delete=models.CASCADE, related_name='items')
    """

    def __init__(self, for_fields=None, *args, **kwargs):
        self.for_fields = for_fields
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        if getattr(model_instance, self.attname) is None:
            # текущее значение отсутствует
            try:
                qs = self.model.objects.all()
                if self.for_fields:
                    # фильтровать по объектам с
                    # одинаковыми значениями полей
                    # для полей в "for_fields"
                    query = {field: getattr(model_instance, field)\
                    for field in self.for_fields}
                    qs = qs.filter(**query)
                # получить порядок последней позиции
                last_item = qs.latest(self.attname)
                value = last_item.order + 1
            except ObjectDoesNotExist:
                value = 0
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super().pre_save(model_instance, add)
