from django.db.models.base import Model
import markdown
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords_html
from django.urls import reverse_lazy

from .models import Post


class LatestPostsFeed(Feed):
    """Новостная лента."""

    title = 'Мой блог'
    link = reverse_lazy('blog:post_list')
    description = 'Новая статья в блоге'

    def items(self):
        return Post.published.all()[:3]
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        return truncatewords_html(markdown.markdown(item.body), 30)
    
    def item_pubdate(self, item):
        return item.publish
