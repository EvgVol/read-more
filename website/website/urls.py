from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.utils.translation import gettext_lazy as _

from blog.sitemaps import PostSitemap


sitemaps = {
    'posts': PostSitemap
}

handler400 = 'core.views.bad_request'
handler401 = 'core.views.unauthorized'
handler403 = 'core.views.permission_denied'
handler404 = 'core.views.page_not_found'
handler500 = 'core.views.server_error'
handler503 = 'core.views.server_unavailable'

urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls, name='admin'),
    path('', include('account.urls')),
    path('auth/', include('social_django.urls', namespace='social')),
    path('', include('core.urls', namespace='core')),
    path(_('blog/'), include('blog.urls', namespace='blog')),
    path(_('vookmarks/'), include('vookmarks.urls', namespace='vookmarks')),
    path('', include('actions.urls', namespace='actions')),
    path('', include('reviews.urls', namespace='reviews')),
    path(_('shop/'), include('shop.urls', namespace='shop')),
    path(_('cart/'), include('cart.urls', namespace='cart')),
    path(_('coupons/'), include('coupons.urls', namespace='coupons')),
    path(_('orders/'), include('orders.urls', namespace='orders')),
    path(_(''), include('courses.urls', namespace='courses')),
    path(_('chat/'), include('chat.urls', namespace='chat')),
    path(_('api/'), include('courses.api.urls', namespace='api')),
    path('rosetta/', include('rosetta.urls')),
    path('__debug__/', include('debug_toolbar.urls', namespace='debug')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
)

if settings.DEBUG:
    
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
