from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _

from taggit.managers import TaggableManager
from pytils.translit import slugify


class Category(models.Model):
    """Model for categories of blog posts."""

    name = models.CharField(_('name'), max_length=50)
    slug = models.SlugField(_('slug'), unique=True)

    class Meta:
        ordering = ['-name']
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        """Overrides the save method to auto-generate slug."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:post_list_by_category', args=[self.slug])
    

class PublishManager(models.Manager):
    """
    Manager for retrieving published posts.

    This manager extends the default manager for the Post model to only return
    posts that have the PUBLISHED status.
    """
    def get_queryset(self) -> QuerySet:
        """
        Returns a queryset containing only published posts.
        """
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Post(models.Model):
    """Model representing a blog post."""

    class Status(models.TextChoices):
        """Choices for the status of the blog post."""

        DRAFT = 'DF', _('draft')
        PUBLISHED = 'PB', _('published')

    title = models.CharField(
        _('title'),
        max_length=250,
        help_text=_('Enter the title of the blog post.')
    )
    slug = models.SlugField(
        _('slug'),
        max_length=50,
        unique_for_date='publish',
        help_text=_('Enter a URL-friendly slug for the blog post.')
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_posts',
        verbose_name=_('author'),
    )
    body = models.TextField(_('content'))
    tags = TaggableManager()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 null=True, blank=False,
                                 related_name='posts',
                                 verbose_name=_('category'))
    image = models.ImageField(_('image'), upload_to='blog/images/',)
    publish = models.DateTimeField(_('publish'), default=timezone.now)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    status = models.CharField(_('status'),
                              max_length=2,
                              choices=Status.choices,
                              default=Status.PUBLISHED)
    objects = models.Manager()
    published = PublishManager()
    users_like = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                        verbose_name = _('liked'),
                                        related_name='posts_liked',
                                        blank=True)

    class Meta:
        ordering = ['-publish']
        verbose_name = _('post')
        verbose_name_plural = _('posts')
        indexes = [
            models.Index(fields=['-publish']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Returns the URL for the blog post."""
        return reverse('blog:post_detail',
                       args=[self.publish.year,
                             self.publish.month,
                             self.publish.day,
                             self.slug])


class Comment(models.Model):
    """
    Model for comments.
    This model represents a comment left by a user on a specific blog post.
    """

    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments',
                             verbose_name = _('post'))
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               verbose_name=_("author"),
                               related_name='comments',
                               on_delete=models.CASCADE)
    body = models.TextField(
        _('message'),
        help_text=_('Enter your comment.')
    )
    created = models.DateTimeField(
        _('created'),
        auto_now_add=True)
    updated = models.DateTimeField(
        _('updated'),
        auto_now=True)
    active = models.BooleanField(
        default=True,
        verbose_name = _('active'),
        help_text=_(
            'A boolean field indicating whether the comment is active.'
        )
    )

    class Meta:
        ordering = ['created']
        verbose_name = _('comment')
        verbose_name_plural = _('comments')
        indexes = [
            models.Index(fields=['created']),
        ]
    
    def __str__(self):
        return force_str(_(f'Comment from {self.name} on post "{self.post}"'))
