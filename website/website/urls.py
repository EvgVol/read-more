from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from blog.sitemaps import PostSitemap

sitemaps = {
    'posts': PostSitemap
}

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', include('account.urls')),
    path('auth/', include('social_django.urls', namespace='social')),
    path('', include('core.urls', namespace='core')),
    path('blog/', include('blog.urls', namespace='blog')),
    path('vookmarks/', include('vookmarks.urls', namespace='vookmarks')),
    path('', include('actions.urls', namespace='actions')),
    path('shop/', include('shop.urls', namespace='shop')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('__debug__/', include('debug_toolbar.urls', namespace='debug')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )