from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import imghdr


def validate_svg_image(upload):
    valid_formats = ['svg']
    # Получить расширение файла
    file_extension = upload.name.split('.')[-1].lower()
    # Проверить расширение файла
    if file_extension not in valid_formats or imghdr.what(upload) != 'svg':
        raise ValidationError(
            _(f"The file format '{file_extension}' is not supported. Please upload a valid SVG image.")
        )
