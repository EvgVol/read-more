from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from taggit.managers import TaggableManager
from pytils.translit import slugify


class Category(models.Model):
    """
    Model for categories of blog posts.
    
    Args:
        models (django.db.models.Model): Django model class.
    
    Attributes:
        name (str): Name of the category.
        slug (str): Slug for the category.
    
    Meta:
        ordering (list): Default ordering for the model.
        verbose_name (str): Singular display name of the model.
        verbose_name_plural (str): Plural display name of the model.
    
    Methods:
        __str__(self) -> str:
            Returns the name of the category.
        
        save(self, *args, **kwargs):
            Overrides the save method to auto-generate slug.
        
        get_absolute_url(self) -> str:
            Returns the URL for the post list with this category.
    """

    name = models.CharField(_('name'), max_length=50)
    slug = models.SlugField(_('slug'), unique=True)

    class Meta:
        ordering = ['-name']
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def __str__(self) -> str:
        """
        Returns the name of the category.
        
        Returns:
            str: Name of the category.
        """
        return self.name

    def save(self, *args, **kwargs):
        """
        Overrides the save method to auto-generate slug.
        
        Args:
            *args: Positional arguments for the save method.
            **kwargs: Keyword arguments for the save method.
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """
        Returns the URL for the post list with this category.
        
        Returns:
            str: URL for the post list with this category.
        """
        return reverse('blog:post_list_by_category', args=[self.slug])
    

class PublishManager(models.Manager):
    """
    Manager for retrieving published posts.

    This manager extends the default manager for the Post model to only return
    posts that have the PUBLISHED status.

    Methods:
        get_queryset(): Returns a queryset containing only published posts.
    """
    def get_queryset(self) -> QuerySet:
        """
        Returns a queryset containing only published posts.
        """
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Post(models.Model):
    """Model representing a blog post.

    Attributes:
        title (str): Title of the blog post.
        slug (str): Slug for the blog post URL.
        author (User): User representing the author of the blog post.
        body (str): Body of the blog post.
        tags (TaggableManager): Manager for tags related to the blog post.
        category (Category): Category for the blog post.
        image (ImageField): Image associated with the post.
        publish (datetime): Date and time the blog post was published.
        created (datetime): Date and time the blog post was created.
        updated (datetime): Date and time the blog post was last updated.
        status (str): Status of the blog post.
        objects (Manager): Manager for accessing the database.
        published (PublishManager): Manager for published blog posts.
        users_like (ManyToManyField): Users who have liked the blog post.
    """

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

    Attributes:
        post (ForeignKey): A reference to the post that the comment is 
            associated with.
        name (CharField): The name of the user who left the comment.
        email (EmailField): The email address of the user who left 
            the comment.
        body (TextField): The text of the comment.
        created (DateTimeField): The date and time that the comment was 
            created.
        updated (DateTimeField): The date and time that the comment was 
            last updated.
        active (BooleanField): A boolean field indicating whether the 
            comment is active.
    """

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name = _('post'),
        help_text=_('Select a post to associate the comment with.')
    )
    name = models.CharField(
        _('username'),
        max_length=80,
        help_text=_('Enter your name.')
    )
    email = models.EmailField(
        _('email'),
        help_text=_('Enter your email address.')
    )
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
        return _(f'Comment from {self.name} on post "{self.post}"')
