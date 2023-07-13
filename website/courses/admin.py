from django.contrib import admin
from django.db import models
from django.forms import SelectMultiple
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from courses.models import subject, course, module, advantage, technology
from .forms import CourseForm

@admin.register(advantage.Advantage)
class AdvantageAdmin(admin.ModelAdmin):
    
    list_display = ('image_tag','name',)
    
    def image_tag(self, obj):
        return format_html(
            '<img src="{}" width="50" height="50" />'
            .format(obj.image.url)
        )

    image_tag.short_description = 'Image'


@admin.register(technology.Technology)
class TechnologyAdmin(admin.ModelAdmin):
    
    list_display = ('image_tag', 'name', 'hints')
    search_fields = ['name']
    
    def image_tag(self, obj):
        return format_html(
            '<img src="{}" width="50" height="50" />'
            .format(obj.url)
        )

    image_tag.short_description = 'Image'


@admin.register(subject.Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}


class ModuleInLine(admin.StackedInline):
    model = module.Module


@admin.register(course.Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['icon_course','title', 'subject', 'created',
                    'complexity', 'get_technologies', 'period',
                    'count_projects']
    list_filter = ['created', 'subject', 'load', 'technologies']
    search_fields = ['title', 'overview']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInLine]
    filter_horizontal = ('technologies', 'advantages', 'cards')
    form = CourseForm

    @admin.display(description=_('technologies'))
    def get_technologies(self, obj):
        return ',\n '.join([ 
            f'{item.name}'
            for item in obj.technologies.all()])

    @admin.display(description=_('icon course'))
    def icon_course(self, obj):
        return format_html(
            '<img src="{}" width="100" height="70" />'
            .format(obj.image.url)
        )

@admin.register(course.Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['title', 'course']
