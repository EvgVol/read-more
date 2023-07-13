from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.encoding import force_str


class Review(models.Model):
    """
    Model representing a review for a specific object.
    
    Attributes:
        author (ForeignKey): The author of the review.
        content_type (ForeignKey): The content type of the related object.
        object_id (PositiveIntegerField): The ID of the related object.
        content_object (GenericForeignKey): The related object.
        rating (PositiveIntegerField): The rating given in the review.
        comment (TextField): The comment left in the review.
        created (DateTimeField): The date and time when the review was created.
        updated (DateTimeField): The date and time when the review was last updated.
    """
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               verbose_name=_('author'),
                               on_delete=models.CASCADE,
                               related_name='reviews')
    content_type = models.ForeignKey(ContentType,
                                     verbose_name=_('content type'),
                                     on_delete=models.CASCADE,
                                     related_name='reviews',
                                     db_index=True)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    rating = models.PositiveIntegerField(blank=True)
    comment = models.TextField(_('comment'), blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name=_('review')
        verbose_name_plural=_('reviews')

    def clean(self):
        if self.rating is None and self.comment == '':
            raise ValidationError(
                _("Rating and comment cannot both be empty.")
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return force_str(_(f'{self.author} left a review'))
