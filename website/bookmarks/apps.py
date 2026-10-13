from django.apps import AppConfig


class BookmarksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bookmarks'
    verbose_name = 'Визуальные закладки'

    def ready(self):
        import bookmarks.signals